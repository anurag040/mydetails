package com.projectforge.aipg.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * Database schema definition
 */
public class DatabaseSchema {
    private List<Entity> entities;
    private List<Relationship> relationships;
    
    public DatabaseSchema() {}
    
    public List<Entity> getEntities() { return entities; }
    public void setEntities(List<Entity> entities) { this.entities = entities; }
    
    public List<Relationship> getRelationships() { return relationships; }
    public void setRelationships(List<Relationship> relationships) { this.relationships = relationships; }
    
    public static class Entity {
        private String name;
        private String tableName;
        private List<Field> fields;
        private List<String> indexes;
        
        public Entity() {}
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getTableName() { return tableName; }
        public void setTableName(String tableName) { this.tableName = tableName; }
        
        public List<Field> getFields() { return fields; }
        public void setFields(List<Field> fields) { this.fields = fields; }
        
        public List<String> getIndexes() { return indexes; }
        public void setIndexes(List<String> indexes) { this.indexes = indexes; }
    }
    
    public static class Field {
        private String name;
        private String type;
        private boolean nullable;
        private boolean primaryKey;
        private String defaultValue;
        private Map<String, Object> constraints;
        
        public Field() {}
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public boolean isNullable() { return nullable; }
        public void setNullable(boolean nullable) { this.nullable = nullable; }
        
        public boolean isPrimaryKey() { return primaryKey; }
        public void setPrimaryKey(boolean primaryKey) { this.primaryKey = primaryKey; }
        
        public String getDefaultValue() { return defaultValue; }
        public void setDefaultValue(String defaultValue) { this.defaultValue = defaultValue; }
        
        public Map<String, Object> getConstraints() { return constraints; }
        public void setConstraints(Map<String, Object> constraints) { this.constraints = constraints; }
    }
    
    public static class Relationship {
        private String type;
        private String fromEntity;
        private String toEntity;
        private String fromField;
        private String toField;
        
        public Relationship() {}
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public String getFromEntity() { return fromEntity; }
        public void setFromEntity(String fromEntity) { this.fromEntity = fromEntity; }
        
        public String getToEntity() { return toEntity; }
        public void setToEntity(String toEntity) { this.toEntity = toEntity; }
        
        public String getFromField() { return fromField; }
        public void setFromField(String fromField) { this.fromField = fromField; }
        
        public String getToField() { return toField; }
        public void setToField(String toField) { this.toField = toField; }
    }
}
