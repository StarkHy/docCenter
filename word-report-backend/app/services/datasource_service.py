import os
import json
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import DataSource
from app.repositories.datasource_repository import DataSourceRepository


class DataSourceService:
    def __init__(self):
        self.storage_path = settings.DATA_SOURCE_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    async def get_datasources(self, session: AsyncSession, type_filter: Optional[str] = None) -> List[dict]:
        database_types = {'kingbase', 'mysql', 'oracle', 'postgresql'}
        datasource_types = {'http_api', 'json', 'form', 'sql'}
        
        repo = DataSourceRepository(session)
        all_datasources = await repo.get_all()
        
        if type_filter == 'database':
            datasources = [ds for ds in all_datasources if ds.type in database_types]
        elif type_filter == 'datasource':
            datasources = [ds for ds in all_datasources if ds.type in datasource_types]
        else:
            datasources = all_datasources
        
        return [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "config": ds.config or {},
                "status": ds.status,
                "create_time": ds.create_time.strftime("%Y-%m-%d %H:%M:%S") if ds.create_time else ""
            }
            for ds in sorted(datasources, key=lambda x: x.id)
        ]

    async def get_datasource(self, ds_id: int, session: AsyncSession) -> Optional[dict]:
        repo = DataSourceRepository(session)
        ds = await repo.get_by_id(ds_id)
        if not ds:
            return None
        config = ds.config or {}
        result_dict = {
            "id": ds.id,
            "name": ds.name,
            "type": ds.type,
            "config": config,
            "status": ds.status,
            "create_time": ds.create_time.strftime("%Y-%m-%d %H:%M:%S") if ds.create_time else ""
        }
        for key in ["username", "password"]:
            if key in config:
                result_dict[key] = config[key]
        return result_dict

    async def create_datasource(self, data: dict, session: AsyncSession) -> dict:
        repo = DataSourceRepository(session)
        all_datasources = await repo.get_all()
        max_id = max((ds.id for ds in all_datasources), default=0)
        new_id = max_id + 1
        
        ds_type = data.get("type", "")
        config = data.get("config", {})
        config = self.enrich_config_with_fields(ds_type, config)

        ds = DataSource(
            id=new_id,
            name=data["name"],
            type=ds_type,
            config=config,
            status="unknown"
        )
        session.add(ds)
        await session.commit()
        await session.refresh(ds)

        return {
            "id": ds.id,
            "name": ds.name,
            "type": ds.type,
            "status": ds.status,
            "create_time": ds.create_time.strftime("%Y-%m-%d %H:%M:%S") if ds.create_time else ""
        }

    async def update_datasource(self, ds_id: int, data: dict, session: AsyncSession) -> Optional[dict]:
        repo = DataSourceRepository(session)
        ds = await repo.get_by_id(ds_id)
        if not ds:
            return None

        ds.name = data.get("name", ds.name)
        ds.type = data.get("type", ds.type)
        
        config = data.get("config", ds.config)
        ds_type = data.get("type", ds.type)
        if config:
            config = self.enrich_config_with_fields(ds_type, config)
        ds.config = config
        
        await session.commit()
        await session.refresh(ds)

        return {
            "id": ds.id,
            "name": ds.name,
            "type": ds.type,
            "status": ds.status,
            "create_time": ds.create_time.strftime("%Y-%m-%d %H:%M:%S") if ds.create_time else ""
        }

    async def delete_datasource(self, ds_id: int, session: AsyncSession) -> bool:
        repo = DataSourceRepository(session)
        ds = await repo.get_by_id(ds_id)
        if not ds:
            return False
        await session.delete(ds)
        await session.commit()
        return True

    async def update_datasource_status(self, ds_id: int, status: str, session: AsyncSession) -> bool:
        repo = DataSourceRepository(session)
        ds = await repo.get_by_id(ds_id)
        if not ds:
            return False
        ds.status = status
        await session.commit()
        return True

    async def test_datasource(self, ds: dict, session: AsyncSession = None) -> dict:
        ds_type = ds.get("type")
        config = ds.get("config", {})

        if ds_type == "http_api":
            return self._test_http_api(config)
        elif ds_type == "json":
            return self._test_json(config)
        elif ds_type == "form":
            return self._test_form(config)
        elif ds_type == "kingbase":
            return self._test_kingbase(config)
        elif ds_type == "postgresql":
            return self._test_postgresql(config)
        elif ds_type == "mysql":
            return self._test_mysql(config)
        elif ds_type == "oracle":
            return self._test_oracle(config)
        elif ds_type == "sql":
            if not session:
                return {"success": False, "message": "SQL 类型测试需要数据库会话"}
            return await self._test_sql(config, session)
        else:
            raise ValueError(f"不支持的数据源类型: {ds_type}")

    def _test_http_api(self, config: dict) -> dict:
        try:
            method = config.get("method", "GET").upper()
            url = config.get("url", "")
            raw_headers = config.get("headers", [])
            raw_params = config.get("params", [])
            body = config.get("body", {})
            parameters = config.get("parameters", [])

            if not url:
                raise ValueError("请配置接口地址")

            url = self._substitute_params_in_string(url, parameters)
            
            headers = {}
            if isinstance(raw_headers, list):
                for h in raw_headers:
                    if isinstance(h, dict) and h.get("key"):
                        headers[h["key"]] = h.get("value", "")
            elif isinstance(raw_headers, dict):
                headers = self._substitute_params_in_dict(raw_headers, parameters)
            
            params = {}
            if isinstance(raw_params, list):
                for p in raw_params:
                    if isinstance(p, dict) and p.get("key"):
                        params[p["key"]] = p.get("value", "")
            elif isinstance(raw_params, dict):
                params = self._substitute_params_in_dict(raw_params, parameters)
            
            params = self._substitute_params_in_dict(params, parameters)
            
            if isinstance(body, str):
                body = self._substitute_params_in_string(body, parameters)
            elif isinstance(body, dict):
                body = self._substitute_params_in_dict(body, parameters)

            timeout = config.get("timeout", 10)

            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=timeout, verify=False)
            elif method == "POST":
                if isinstance(body, dict):
                    response = requests.post(url, headers=headers, params=params, json=body, timeout=timeout, verify=False)
                else:
                    response = requests.post(url, headers=headers, params=params, data=body, timeout=timeout, verify=False)
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            try:
                response_data = response.json()
            except:
                response_data = response.text

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response_data,
                "message": "连接成功"
            }
        except requests.exceptions.Timeout:
            return {"success": False, "message": "请求超时"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"请求失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _substitute_params_in_string(self, text: str, params: list) -> str:
        if not text or not params:
            return text
        
        param_defaults = {}
        for param in params:
            param_name = param.get("name", "")
            default_value = param.get("default", "")
            
            if not param_name:
                continue
            
            param_defaults[param_name] = str(default_value) if default_value else ""
        
        for param_name, default_value in param_defaults.items():
            param_placeholder = f":{param_name}"
            text = text.replace(param_placeholder, default_value)
        
        return text

    def _substitute_params_in_dict(self, data: dict, params: list) -> dict:
        if not data or not params:
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._substitute_params_in_string(value, params)
            else:
                result[key] = value
        return result

    def _parse_sql_params(self, sql: str) -> list:
        """Parse parameters from SQL query string.
        
        Supports:
        - PostgreSQL: $1, $2, $3...
        - Named: :name, @name
        - ODBC: ?
        """
        if not sql:
            return []
        
        import re
        params = []
        seen = set()
        
        # Match $1, $2, $3... (PostgreSQL positional)
        for match in re.finditer(r'\$(\d+)', sql):
            param_name = f"param_{match.group(1)}"
            if param_name not in seen:
                seen.add(param_name)
                params.append({
                    "name": param_name,
                    "type": "string",
                    "label": param_name,
                    "required": True,
                    "default": ""
                })
        
        # Match :name or @name (named parameters)
        for match in re.finditer(r'[:@]([a-zA-Z_][a-zA-Z0-9_]*)', sql):
            param_name = match.group(1)
            if param_name not in seen:
                seen.add(param_name)
                params.append({
                    "name": param_name,
                    "type": "string",
                    "label": param_name,
                    "required": True,
                    "default": ""
                })
        
        # Match ? (ODBC positional)
        question_marks = sql.count('?')
        for i in range(question_marks):
            param_name = f"param_{i+1}"
            if param_name not in seen:
                seen.add(param_name)
                params.append({
                    "name": param_name,
                    "type": "string",
                    "label": param_name,
                    "required": True,
                    "default": ""
                })
        
        return params

    def _test_json(self, config: dict) -> dict:
        try:
            json_text = config.get("json_text", "")
            if not json_text:
                raise ValueError("请输入JSON文本")

            data = json.loads(json_text)

            return {
                "success": True,
                "data": data,
                "message": "JSON解析成功"
            }
        except json.JSONDecodeError as e:
            return {"success": False, "message": f"JSON格式错误: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _test_form(self, config: dict) -> dict:
        try:
            fields = config.get("fields", {})

            return {
                "success": True,
                "data": fields,
                "message": "表单数据有效"
            }
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _test_kingbase(self, config: dict) -> dict:
        try:
            import psycopg2
            host = config.get("host", "")
            port = config.get("port", "54321")
            database = config.get("database", "")
            user = config.get("user", "")
            password = config.get("password", "")
            sql = config.get("test_sql", "SELECT 1")

            if not host or not database:
                raise ValueError("请配置主机地址、端口和数据库名")

            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version()")
            version_row = cur.fetchone()
            version = version_row[0] if version_row else "Unknown"
            
            cur.execute(sql)
            rows = cur.fetchall()
            
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            conn.close()

            return {
                "success": True,
                "message": "数据库连接成功",
                "data": {
                    "version": version,
                    "columns": columns,
                    "rows": rows[:10],
                    "row_count": len(rows)
                }
            }
        except ImportError:
            return {"success": False, "message": "请安装 psycopg2-binary 库: pip install psycopg2-binary"}
        except psycopg2.Error as e:
            return {"success": False, "message": f"数据库错误: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _test_postgresql(self, config: dict) -> dict:
        try:
            import psycopg2
            host = config.get("host", "")
            port = config.get("port", "5432")
            database = config.get("database", "")
            user = config.get("user", "")
            password = config.get("password", "")
            sql = config.get("test_sql", "SELECT 1")

            if not host or not database:
                raise ValueError("请配置主机地址、端口和数据库名")

            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version()")
            version_row = cur.fetchone()
            version = version_row[0] if version_row else "Unknown"
            
            cur.execute(sql)
            rows = cur.fetchall()
            
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            conn.close()

            params = self._parse_sql_params(sql)
            return {
                "success": True,
                "message": "数据库连接成功",
                "data": {
                    "version": version,
                    "columns": columns,
                    "rows": rows[:10],
                    "row_count": len(rows),
                    "params": params
                }
            }
        except ImportError:
            return {"success": False, "message": "请安装 psycopg2-binary 库: pip install psycopg2-binary"}
        except psycopg2.Error as e:
            return {"success": False, "message": f"数据库错误: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}
    
    def _test_mysql(self, config: dict) -> dict:
        try:
            import pymysql
            host = config.get("host", "")
            port = config.get("port", "3306")
            database = config.get("database", "")
            user = config.get("user", "")
            password = config.get("password", "")
            sql = config.get("test_sql", "SELECT 1")

            if not host or not database:
                raise ValueError("请配置主机地址、端口和数据库名")

            conn = pymysql.connect(
                host=host,
                port=int(port),
                database=database,
                user=user,
                password=password
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version()")
            version_row = cur.fetchone()
            version = version_row[0] if version_row else "Unknown"
            
            cur.execute(sql)
            rows = cur.fetchall()
            
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            conn.close()

            return {
                "success": True,
                "message": "数据库连接成功",
                "data": {
                    "version": version,
                    "columns": columns,
                    "rows": rows[:10],
                    "row_count": len(rows)
                }
            }
        except ImportError:
            return {"success": False, "message": "请安装 psycopg2-binary 库: pip install psycopg2-binary"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _test_mysql(self, config: dict) -> dict:
        try:
            import pymysql
            host = config.get("host", "")
            port = config.get("port", "3306")
            database = config.get("database", "")
            user = config.get("user", "")
            password = config.get("password", "")
            sql = config.get("test_sql", "SELECT 1")

            if not host or not database:
                raise ValueError("请配置主机地址、端口和数据库名")

            conn = pymysql.connect(
                host=host,
                port=int(port),
                database=database,
                user=user,
                password=password
            )
            
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            conn.close()

            params = self._parse_sql_params(sql)
            return {
                "success": True,
                "message": "数据库连接成功",
                "data": {
                    "columns": columns,
                    "rows": rows[:10],
                    "row_count": len(rows),
                    "params": params
                }
            }
        except ImportError:
            return {"success": False, "message": "请安装 pymysql 库: pip install pymysql"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    def _test_oracle(self, config: dict) -> dict:
        try:
            import cx_Oracle
            host = config.get("host", "")
            port = config.get("port", "1521")
            service_name = config.get("service_name", "")
            service = config.get("service", "")
            user = config.get("user", "")
            password = config.get("password", "")
            sql = config.get("test_sql", "SELECT 1 FROM DUAL")

            if not (service_name or service) or not user:
                raise ValueError("请配置服务名/连接串和用户名")

            if service:
                dsn = service
            else:
                dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

            conn = cx_Oracle.connect(user, password, dsn)
            
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            conn.close()

            return {
                "success": True,
                "message": "数据库连接成功",
                "data": {
                    "columns": columns,
                    "rows": rows[:10],
                    "row_count": len(rows)
                }
            }
        except ImportError:
            return {"success": False, "message": "请安装 cx-Oracle 库: pip install cx-Oracle"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}

    async def _test_sql(self, config: dict, session: AsyncSession) -> dict:
        try:
            database_id = config.get("database_id")
            main_sql = config.get("sql", "")
            params = config.get("params", [])
            
            if not database_id:
                return {"success": False, "message": "请先选择数据库"}
            
            from app.models import Database
            db_config = await session.get(Database, database_id)
            
            if not db_config:
                return {"success": False, "message": f"找不到数据库配置 (ID: {database_id})"}
            
            db_type = db_config.db_type
            db_conn_config = {
                "host": db_config.host,
                "port": db_config.port,
                "database": db_config.database,
                "user": db_config.user,
                "password": db_config.password,
                "service_name": db_config.service_name
            }
            db_test_sql = db_config.test_sql or "SELECT 1"
            
            if db_type == "kingbase":
                conn_result = self._test_kingbase({**db_conn_config, "test_sql": db_test_sql})
            elif db_type == "postgresql":
                conn_result = self._test_postgresql({**db_conn_config, "test_sql": db_test_sql})
            elif db_type == "mysql":
                conn_result = self._test_mysql({**db_conn_config, "test_sql": db_test_sql})
            elif db_type == "oracle":
                conn_result = self._test_oracle({**db_conn_config, "test_sql": db_test_sql})
            else:
                return {"success": False, "message": f"不支持的数据库类型: {db_type}"}
            
            if not conn_result.get("success"):
                return conn_result
            
            if not main_sql:
                return conn_result
            
            main_sql = self._substitute_sql_params(main_sql, params)
            
            if db_type == "kingbase":
                result = self._test_kingbase({**db_conn_config, "test_sql": main_sql})
            elif db_type == "postgresql":
                result = self._test_postgresql({**db_conn_config, "test_sql": main_sql})
            elif db_type == "mysql":
                result = self._test_mysql({**db_conn_config, "test_sql": main_sql})
            elif db_type == "oracle":
                result = self._test_oracle({**db_conn_config, "test_sql": main_sql})
            
            if result.get("success") and params:
                if "data" not in result:
                    result["data"] = {}
                result["data"]["params"] = params
            
            return result
                
        except Exception as e:
            return {"success": False, "message": f"SQL 测试失败: {str(e)}"}

    def _substitute_sql_params(self, sql: str, params: list) -> str:
        if not params:
            return sql
        
        import re
        
        for param in params:
            param_name = param.get("name", "")
            default_value = param.get("default", "")
            param_type = param.get("type", "string")
            
            if not param_name:
                continue
            
            param_placeholder = f":{param_name}"
            
            if param_placeholder not in sql:
                continue
            
            if default_value:
                if param_type == "date":
                    sql = sql.replace(param_placeholder, f"'{default_value}'")
                elif param_type == "integer":
                    sql = sql.replace(param_placeholder, str(default_value))
                else:
                    sql = sql.replace(param_placeholder, f"'{default_value}'")
            else:
                if param_type == "integer":
                    sql = sql.replace(param_placeholder, "0")
                else:
                    sql = sql.replace(param_placeholder, "''")
        
        return sql
    
    async def get_datasource_params(self, ds_ids: List[int], session: AsyncSession) -> List[dict]:
        params_map = {}
        
        for ds_id in ds_ids:
            ds = await self.get_datasource(ds_id, session)
            if not ds:
                continue
            
            ds_type = ds.get("type")
            config = ds.get("config", {})
            
            if ds_type in ("kingbase", "postgresql", "mysql", "oracle", "sql"):
                params = config.get("params", [])
                for p in params:
                    param_name = p.get("name", "")
                    if param_name and param_name not in params_map:
                        params_map[param_name] = {
                            "name": param_name,
                            "type": p.get("type", "string"),
                            "label": p.get("label", param_name),
                            "required": p.get("required", True),
                            "default": p.get("default", ""),
                            "datasource_id": ds_id,
                            "datasource_name": ds.get("name")
                        }
            elif ds_type == "http_api":
                parameters = config.get("parameters", [])
                for p in parameters:
                    param_name = p.get("name", "")
                    if param_name and param_name not in params_map:
                        params_map[param_name] = {
                            "name": param_name,
                            "type": p.get("type", "string"),
                            "label": p.get("label", param_name),
                            "required": p.get("required", True),
                            "default": p.get("default", ""),
                            "datasource_id": ds_id,
                            "datasource_name": ds.get("name")
                        }
        
        return list(params_map.values())
    
    def parse_fields_from_config(self, ds_type: str, config: dict) -> List[str]:
        import re
        if ds_type == 'form':
            return list(config.get('fields', {}).keys())
        elif ds_type == 'json':
            try:
                data = json.loads(config.get('json_text', '{}'))
                if isinstance(data, list):
                    return list(data[0].keys()) if data and isinstance(data[0], dict) else []
                elif isinstance(data, dict):
                    return list(data.keys())
                return []
            except:
                return []
        elif ds_type in ['postgresql', 'kingbase', 'mysql', 'oracle', 'sql']:
            sql = config.get('test_sql') or config.get('sql', '')
            if not sql:
                return []
            match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE)
            if match:
                fields = match.group(1).split(',')
                return [s.strip().split()[-1] for s in fields if s.strip()]
            return ['result']
        return []
    
    def enrich_config_with_fields(self, ds_type: str, config: dict) -> dict:
        config = dict(config)
        fields = self.parse_fields_from_config(ds_type, config)
        config['_fields'] = fields
        return config


data_source_service = DataSourceService()