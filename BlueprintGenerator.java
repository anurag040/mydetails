package com.example.projectforge.ai;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.module.blackbird.BlackbirdModule;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.apache.tika.Tika;

import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * Reads a PRD (text or file) and produces a deterministic JSON "blueprint"
 * describing entities, APIs, pages, and optional dashboards.
 *
 * Requires:
 * - Spring Boot 3.3+
 * - spring-ai-openai-spring-boot-starter
 * - Apache Tika (for file->text)
 *
 * Set OPENAI key (e.g., env var): OPENAI_API_KEY
 */
@Service
public class BlueprintGenerator {

    private static final String SYSTEM_PROMPT = """
      You are a senior full-stack architect. From the PRD below, output JSON ONLY (no prose).
      The JSON MUST match this schema exactly:

      {
        "app": { "name": "kebab-case-short-name", "angularVersion": "17|18", "database": "oracle|vertica|both" },
        "datasources": {
          "oracle": {"url": "", "username": "", "password": ""},
          "vertica": {"url": "", "username": "", "password": ""}
        },
        "entities": [
          {
            "name": "Customer",
            "table": "CUSTOMERS",
            "fields": [
              {"name": "ID", "sqlType": "NUMBER", "pk": true,  "required": true},
              {"name": "NAME", "sqlType": "VARCHAR2(120)", "pk": false, "required": true},
              {"name": "EMAIL","sqlType": "VARCHAR2(180)", "pk": false, "required": false}
            ],
            "apis": [
              {"method":"GET","path":"/api/customers","sql":"SELECT ID,NAME,EMAIL FROM CUSTOMERS ORDER BY ID","params":[]},
              {"method":"POST","path":"/api/customers","sql":"INSERT INTO CUSTOMERS(NAME,EMAIL) VALUES(?,?)","params":["NAME","EMAIL"]}
            ]
          }
        ],
        "pages": [
          {"type":"list","entity":"Customer","route":"/customers"},
          {"type":"form","entity":"Customer","route":"/customers/new"}
        ],
        "dashboards": [
          {
            "route": "/dashboards/sales",
            "title": "Sales Dashboard",
            "widgets": [
              {
                "type":"kpi","title":"Total Revenue (30d)",
                "endpoint":"/api/dash/sales/total-revenue",
                "sql":"SELECT SUM(amount) AS total_revenue FROM fact_payments WHERE paid_at >= NOW() - INTERVAL '30 DAY';",
                "seriesKey":"total_revenue","params":[]
              }
            ]
          }
        ]
      }

      Rules:
      - JSON ONLY. No markdown, no comments, no prose.
      - Use JDBC-ready SQL with '?' placeholders and provide 'params' in order when applicable.
      - For Oracle tables use NUMBER, VARCHAR2(n), DATE, TIMESTAMP. For Vertica use INT, VARCHAR(n), FLOAT/NUMERIC, TIMESTAMP.
      - Keep names consistent across entities, apis, and pages.
      - If the PRD omits something, make reasonable defaults and keep output minimal & coherent.
      """;

    private final ChatClient chat;
    private final ObjectMapper om;
    private final Tika tika = new Tika();

    public BlueprintGenerator(ChatClient chat) {
        this.chat = chat;
        this.om = JsonMapper.builder().addModule(new BlackbirdModule()).build();
    }

    /**
     * Generate blueprint from raw PRD text and user choices.
     *
     * @param prdText full PRD (plain text)
     * @param angularVersion "17" or "18"
     * @param database "oracle" | "vertica" | "both"
     * @param oracleUrl/user/pass optional; pass null/"" if not used
     * @param verticaUrl/user/pass optional; pass null/"" if not used
     */
    public Result generateFromText(
            String prdText,
            String angularVersion,
            String database,
            String oracleUrl, String oracleUser, String oraclePass,
            String verticaUrl, String verticaUser, String verticaPass
    ) {
        String userPrompt = """
          PRD:
          ---
          %s
          ---

          Constraints:
          - Angular version: %s
          - Database(s): %s
          - REST base path: /api
          - Datasource hints (may be placeholders if empty):
            oracle: { "url":"%s","username":"%s","password":"%s" }
            vertica: { "url":"%s","username":"%s","password":"%s" }

          Output:
          - VALID JSON exactly matching the schema. No extra text.
          """.formatted(
                safe(prdText),
                safe(angularVersion),
                safe(database),
                nz(oracleUrl), nz(oracleUser), nz(oraclePass),
                nz(verticaUrl), nz(verticaUser), nz(verticaPass)
        );

        ChatResponse res = chat.prompt()
                .system(SYSTEM_PROMPT)
                .user(userPrompt)
                .call()
                .chatResponse();

        String json = res.getResult().getOutputText();
        Blueprint bp = readBlueprint(json); // throws if invalid
        return new Result(json, bp);
    }

    /**
     * Generate blueprint from an uploaded PRD file (pdf/docx/md/txt).
     */
    public Result generateFromFile(
            MultipartFile prdFile,
            String angularVersion,
            String database,
            String oracleUrl, String oracleUser, String oraclePass,
            String verticaUrl, String verticaUser, String verticaPass
    ) {
        try {
            String text = tika.parseToString(prdFile.getInputStream());
            return generateFromText(text, angularVersion, database,
                    oracleUrl, oracleUser, oraclePass,
                    verticaUrl, verticaUser, verticaPass);
        } catch (Exception e) {
            throw new RuntimeException("Failed to read PRD: " + e.getMessage(), e);
        }
    }

    /**
     * Strict JSON -> Blueprint mapping with a helpful error on failure.
     */
    private Blueprint readBlueprint(String json) {
        try {
            return om.readValue(json.getBytes(StandardCharsets.UTF_8), Blueprint.class);
        } catch (Exception e) {
            throw new RuntimeException("AI did not return valid blueprint JSON. Parse error: "
                    + e.getMessage() + "\nPayload:\n" + json, e);
        }
    }

    private static String nz(String s) { return s == null ? "" : s; }
    private static String safe(String s) { return s == null ? "" : s; }

    // ------------------------------
    // Return type (raw JSON + typed)
    // ------------------------------
    public record Result(String rawJson, Blueprint blueprint) {}

    // ------------------------------
    // Strongly-typed Blueprint model
    // ------------------------------
    public record Blueprint(
            App app,
            Datasources datasources,
            List<Entity> entities,
            List<Page> pages,
            List<Dashboard> dashboards
    ) {
        public record App(String name, String angularVersion, String database) {}
        public record Datasources(Db oracle, Db vertica) { public record Db(String url, String username, String password) {} }
        public record Entity(String name, String table, List<Field> fields, List<Api> apis) {}
        public record Field(String name, String sqlType, boolean pk, boolean required) {}
        public record Api(String method, String path, String sql, List<String> params) {}
        public record Page(String type, String entity, String route) {}
        public record Dashboard(String route, String title, List<Widget> widgets) {
            public record Widget(String type, String title, String endpoint, String sql, List<String> params, String xKey, String yKey, String seriesKey) {}
        }

        public static Blueprint minimal() {
            return new Blueprint(
                    new App("my-app","17","oracle"),
                    new Datasources(new Datasources.Db("","",""), new Datasources.Db("","","")),
                    List.of(),
                    List.of(),
                    List.of()
            );
        }
    }
}




##############
// In any @RestController or @Service
@Autowired BlueprintGenerator generator;

@PostMapping("/api/ai/blueprint")
public Map<String,Object> blueprint(@RequestPart("prdFile") MultipartFile prd,
                                    @RequestParam String angularVersion,
                                    @RequestParam String database,
                                    @RequestParam(required=false) String oracleUrl,
                                    @RequestParam(required=false) String oracleUser,
                                    @RequestParam(required=false) String oraclePass,
                                    @RequestParam(required=false) String verticaUrl,
                                    @RequestParam(required=false) String verticaUser,
                                    @RequestParam(required=false) String verticaPass) {
    var result = generator.generateFromFile(
        prd, angularVersion, database,
        oracleUrl, oracleUser, oraclePass,
        verticaUrl, verticaUser, verticaPass
    );
    // You can return raw JSON string OR the typed object
    return Map.of(
        "raw", result.rawJson(),
        "typed", result.blueprint()
    );
}
##################
<dependencies>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
  <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-jdbc</artifactId></dependency>

  <!-- Spring AI -->
  <dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
    <version>1.0.0-M3</version>
  </dependency>

  <!-- Templating + ZIP + parsing -->
  <dependency><groupId>org.freemarker</groupId><artifactId>freemarker</artifactId></dependency>
  <dependency><groupId>org.apache.commons</groupId><artifactId>commons-compress</artifactId><version>1.26.2</version></dependency>
  <dependency><groupId>org.apache.tika</groupId><artifactId>tika-core</artifactId><version>2.9.2</version></dependency>
  <dependency><groupId>org.apache.tika</groupId><artifactId>tika-parsers-standard-package</artifactId><version>2.9.2</version></dependency>
  <dependency><groupId>org.apache.pdfbox</groupId><artifactId>pdfbox</artifactId><version>3.0.2</version></dependency>
  <dependency><groupId>org.apache.poi</groupId><artifactId>poi-ooxml</artifactId><version>5.2.5</version></dependency>

  <!-- Drivers -->
  <dependency><groupId>com.oracle.database.jdbc</groupId><artifactId>ojdbc11</artifactId><version>23.4.0.24.05</version></dependency>
  <dependency><groupId>com.vertica</groupId><artifactId>vertica-jdbc</artifactId><version>24.1.0-0</version></dependency>

  <dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>
</dependencies>
####################
EPIC A — Foundations & Repo Plumbing
Sprint 1 (Week 1)
A1. Monorepo setup & scaffolding
Desc: Create monorepo with backend/ (Spring Boot) and frontend/ (Angular). Add basic build/run.

AC:

mvn -q -DskipTests package succeeds in /backend

npm i && ng build succeeds in /frontend

Root README.md with dev instructions

Estimate: 4h

Notes: Use Node 18+, Java 17

Deliverables: repo initialized; CI placeholder workflow

A2. Backend base (Web, Validation, JDBC, Tika, Spring AI)
Desc: Add dependencies and a hello endpoint.

AC: /actuator/health and /api/hello return 200

Estimate: 4h

Deliverables: pom.xml, Application.java, HelloController

A3. Dual DataSources (Oracle + Vertica) via Hikari + JdbcTemplate
Desc: Wire oracleJdbc and verticaJdbc beans from application.yml.

AC: App starts with env vars; test queries use each JdbcTemplate

Estimate: 6h

Dependencies: A2

Deliverables: DataSourceConfig.java, sample /api/db/ping

A4. Angular app shell (Material, dark theme, routing)
Desc: Set up Angular 17, Material dark, base routes, proxy to 8080.

AC: ng serve shows shell; API proxy works

Estimate: 6h

Deliverables: styles.scss, app.routes.ts, proxy config

EPIC B — AI Blueprint & Round-Trip JSON
Sprint 2 (Week 2)
B1. PRD ingestion service
Desc: Parse .pdf/.docx/.md/.txt → plain text via Apache Tika.

AC: /api/prd/preview returns first 2k chars

Estimate: 4h

Deliverables: PrdTextExtractor.java

B2. Blueprint generator (strict schema)
Desc: Spring AI class that returns round-trip JSON (requirements + pathStrategy + fileManifest).

AC: /api/ai/blueprint returns valid JSON per schema; fails clearly on invalid

Estimate: 8h

Dependencies: B1, A2

Deliverables: BlueprintGenerator.java, JSON records, JSON Schema (optional)

B3. Path & size validators
Desc: Validate file paths (no .., no absolute), cap files and bytes.

AC: Requests with bad paths/oversized files are rejected with 400 + reason

Estimate: 3h

Deliverables: PathValidator.java, SizeQuota.java

B4. Jobs API (create → status → download)
Desc: Async job controller with in-memory store (to be swapped with queue later).

AC: POST /api/generate returns jobId; /status streams progress; /download streams zip

Estimate: 8h

Dependencies: B1–B3

Deliverables: GenerationController.java, simple job runner

EPIC C — Direct-Files Codegen (No Templates)
Sprint 3 (Week 3)
C1. Manifest prompt & parser
Desc: System + user prompts to produce fileManifest (no code yet); parse into DTO.

AC: PRD → manifest lists all files needed (backend + frontend)

Estimate: 6h

Dependencies: B2

Deliverables: Manifest DTOs, prompt strings

C2. File content prompt (batched)
Desc: System prompt to return full file contents in JSON {files:[{path,language,content}]}.

AC: Batch request (8 files) returns valid JSON with compilable file contents (basic smoke)

Estimate: 8h

Dependencies: C1

Deliverables: AiCodeGenService.getFiles(...)

C3. Writer + zipper
Desc: Write validated files to temp dir; zip entire tree.

AC: Zip contains expected paths; content is exact

Estimate: 4h

Dependencies: B3

Deliverables: FileWriterZipper.java

C4. End-to-end happy path
Desc: Upload PRD → manifest → file batches → zip → download

AC: Sample PRD yields a runnable project skeleton; backend compiles, frontend builds

Estimate: 6h

Dependencies: C1–C3

EPIC D — Build Sandbox, Autofix, and Safety
Sprint 4 (Week 4)
D1. Dockerized build sandbox
Desc: Run backend mvn -q -DskipTests package and frontend npm ci && ng build in ephemeral containers.

AC: Sandbox returns PASS/FAIL + logs; job times out gracefully (e.g., 120s each)

Estimate: 8h

Deliverables: Dockerfile.backend, Dockerfile.frontend, sandbox runner

D2. Autofix loop (single-file repair)
Desc: On compile errors, re-prompt AI with file path + error log to regenerate just that file.

AC: ≥70% of simple build failures fixed automatically on first retry

Estimate: 8h

Dependencies: D1, C2

Deliverables: AutoFixService.java, “fix prompt”

D3. Static checks & allowlists
Desc: Semgrep (Java) + ESLint/TS; dependency allowlist for backend/frontend.

AC: Unknown deps fail generation; lint passes in CI

Estimate: 6h

Deliverables: .semgrep.yml, .eslintrc.cjs, allowlist JSON

D4. Secrets & env handling
Desc: Force ${ENV} placeholders; emit .env.example; refuse hardcoded creds.

AC: Any literal password/url in code triggers rejection

Estimate: 3h

EPIC E — UI/UX: Generator Form & Progress
Sprint 5 (Week 5)
E1. Generator form (Angular)
Desc: Dark theme form for versions, DBs, PRD upload, optional datasource props; sticky “Generate” button.

AC: Form validation; multipart submit; progress card shows live step/status

Estimate: 8h

Deliverables: GeneratorFormComponent, GenerateApiService

E2. Status polling + download
Desc: Poll /status; auto-download zip on COMPLETED.

AC: File downloads with correct name; error toast on FAILED

Estimate: 3h

Dependencies: B4

E3. README preview modal
Desc: After generation, show “How to run” modal with copy-paste commands.

AC: README uses actual package and ports; copy buttons work

Estimate: 2h

EPIC F — Observability & Ops
Sprint 6 (Week 6)
F1. Metrics & logging
Desc: Track: gen time, build time, token usage (if available), retries, success rate.

AC: /actuator/prometheus exposes counters/histograms

Estimate: 6h

F2. Persistence & queue
Desc: Replace in-memory jobs with Postgres (or Redis) + a queue (e.g., RabbitMQ/SQS).

AC: Jobs survive restarts; workers can scale to N replicas

Estimate: 10h

Dependencies: F1, B4

F3. Audit & reproducibility
Desc: Save PRD hash, prompts, responses, model/version, and diffs per jobId (complying with policy).

AC: Admin endpoint lists job lineage; redactions applied

Estimate: 8h

EPIC G — Stretch (Optional)
G1. Hybrid infra templates (safer builds for pom.xml, angular.json, DataSourceConfig, etc.) — 1–2 days

G2. JSON Schema validation for blueprint & file batches — 1 day

G3. Parameterized dashboards & date pickers — 1–2 days

G4. Multi-tenant auth + rate limiting — 2–3 days

Sample Jira Ticket (copy & adapt)
Title: C2 — AI file content generation (batched)
Type: Story
Desc: Implement AiCodeGenService.getFiles(projectName, paths) using Spring AI. Prompt returns JSON with full file contents for a batch of paths.
AC:

Given a manifest with N paths, when requesting any 8 paths, service returns valid JSON with files[].path exactly matching and content non-empty.

Package names in Java files match path.

SQL uses ? placeholders; no string concatenation.

On invalid JSON, service retries once; logs raw payload.
Estimate: 8h
Dependencies: C1
Attachments: Prompts, sample PRD

Environments & Commands (DoD snippets)
Backend run:
OPENAI_API_KEY=... ORACLE_URL=... VERTICA_URL=... mvn spring-boot:run

Frontend run:
npm i && ng serve --proxy-config proxy.conf.json

Sandbox builds:
docker run --rm -v $PWD/backend:/app backend-builder mvn -q -DskipTests package
docker run --rm -v $PWD/frontend:/app frontend-builder npm ci && npm run build

Risk Register (mini)
R1 Model variance → Pin system prompts; cache successful blueprint/file batches.

R2 Token/cost spikes → Batch 8 files; reject >150 files; gzip PRD text; summarize PRD first.

R3 Build flakiness → Hybrid templates for infra + autofix loop for domain files.

R4 Secrets leakage → Env placeholders + scanner; block literals.

R5 Path traversal → Strict sanitizer + allowlist root folders.

