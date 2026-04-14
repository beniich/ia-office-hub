
CREATE TABLE projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE documents (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, filename TEXT, file_path TEXT, file_type TEXT, status TEXT, FOREIGN KEY(project_id) REFERENCES projects(id));
CREATE TABLE ai_diagnostics (id INTEGER PRIMARY KEY AUTOINCREMENT, document_id INTEGER, analysis_type TEXT, interpretation TEXT, recommendations TEXT, confidence_score DECIMAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE presentation_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, structure_json TEXT, style_preference TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE ai_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER, action_performed TEXT, status TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
