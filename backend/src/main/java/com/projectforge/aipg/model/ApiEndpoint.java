package com.projectforge.aipg.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Map;

/**
 * API endpoint definition
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class ApiEndpoint {
    private String path;
    private String method;
    private String description;
    private List<Parameter> parameters;
    private RequestBody requestBody;
    private ResponseBody responseBody;
    private List<String> security;
    
    public ApiEndpoint() {}
    
    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }
    
    public String getMethod() { return method; }
    public void setMethod(String method) { this.method = method; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public List<Parameter> getParameters() { return parameters; }
    public void setParameters(List<Parameter> parameters) { this.parameters = parameters; }
    
    public RequestBody getRequestBody() { return requestBody; }
    public void setRequestBody(RequestBody requestBody) { this.requestBody = requestBody; }
    
    public ResponseBody getResponseBody() { return responseBody; }
    public void setResponseBody(ResponseBody responseBody) { this.responseBody = responseBody; }
    
    public List<String> getSecurity() { return security; }
    public void setSecurity(List<String> security) { this.security = security; }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Parameter {
        private String name;
        private String type;
        private String location;
        private boolean required;
        private String description;
        
        public Parameter() {}
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }
        
        public boolean isRequired() { return required; }
        public void setRequired(boolean required) { this.required = required; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class RequestBody {
        private String contentType;
        private Map<String, Object> schema;
        
        public RequestBody() {}
        
        public String getContentType() { return contentType; }
        public void setContentType(String contentType) { this.contentType = contentType; }
        
        public Map<String, Object> getSchema() { return schema; }
        public void setSchema(Map<String, Object> schema) { this.schema = schema; }
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ResponseBody {
        private String contentType;
        private Map<String, Object> schema;
        
        public ResponseBody() {}
        
        public String getContentType() { return contentType; }
        public void setContentType(String contentType) { this.contentType = contentType; }
        
        public Map<String, Object> getSchema() { return schema; }
        public void setSchema(Map<String, Object> schema) { this.schema = schema; }
    }
}
