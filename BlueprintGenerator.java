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
