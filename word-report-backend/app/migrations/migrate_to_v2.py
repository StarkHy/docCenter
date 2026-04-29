"""
数据库迁移脚本：v1.0 -> v2.0 (JSON 字段 -> 关联表)

迁移内容:
- 创建 mapping_datasources 表
- 创建 mapping_charts 表
- 迁移现有 JSON 数据到新表
- 保留向后兼容性

使用方法:
    cd word-report-backend
    source venv/bin/activate
    python -m app.migrations.migrate_to_v2
"""

import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import DATABASE_URL, async_session


async def migrate_upgrade():
    async with async_session() as session:
        try:
            # 1. 创建新表
            print("[1/6] 创建 mapping_datasources 表...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS mapping_datasources (
                    mapping_id INTEGER NOT NULL,
                    datasource_id INTEGER NOT NULL,
                    "order" INTEGER DEFAULT 0 NOT NULL,
                    PRIMARY KEY (mapping_id, datasource_id),
                    FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
                    FOREIGN KEY (datasource_id) REFERENCES datasources(id) ON DELETE CASCADE
                )
            """))
            
            print("[2/6] 创建 mapping_charts 表...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS mapping_charts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mapping_id INTEGER NOT NULL,
                    chart_id VARCHAR(100) NOT NULL,
                    chart_type VARCHAR(50),
                    chart_title VARCHAR(255),
                    chart_config JSON,
                    FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
                    UNIQUE (mapping_id, chart_id)
                )
            """))
            
            # 创建索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_mapping_charts_chart_id 
                ON mapping_charts(chart_id)
            """))
            
            await session.commit()
            
            # 2. 数据迁移：从 JSON 到新表
            print("[3/6] 迁移 mapping_datasources 数据...")
            result = await session.execute(text("""
                SELECT id, datasource_ids FROM mappings 
                WHERE datasource_ids IS NOT NULL
            """))
            mappings = result.fetchall()
            
            datasources_migrated = 0
            for mapping in mappings:
                if mapping.datasource_ids:
                    try:
                        # 尝试解析 JSON
                        if isinstance(mapping.datasource_ids, str):
                            datasource_ids = json.loads(mapping.datasource_ids)
                        else:
                            datasource_ids = mapping.datasource_ids
                        
                        # 插入关联表
                        for idx, ds_id in enumerate(datasource_ids):
                            await session.execute(text("""
                                INSERT OR IGNORE INTO mapping_datasources 
                                (mapping_id, datasource_id, "order")
                                VALUES (:mapping_id, :datasource_id, :order)
                            """), {
                                "mapping_id": mapping.id,
                                "datasource_id": ds_id,
                                "order": idx
                            })
                            datasources_migrated += 1
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"  ⚠️  警告：Mapping {mapping.id} 的 datasource_ids 解析失败：{e}")
            
            print(f"  ✓ 迁移了 {datasources_migrated} 条数据源关联")
            
            # 3. 迁移图表数据
            print("[4/6] 迁移 mapping_charts 数据...")
            result = await session.execute(text("""
                SELECT id, charts FROM mappings 
                WHERE charts IS NOT NULL
            """))
            mappings = result.fetchall()
            
            charts_migrated = 0
            for mapping in mappings:
                if mapping.charts:
                    try:
                        # 尝试解析 JSON
                        if isinstance(mapping.charts, str):
                            charts = json.loads(mapping.charts)
                        else:
                            charts = mapping.charts
                        
                        # 插入图表配置
                        for chart in charts:
                            chart_id = chart.get('id', f'chart_{charts.index(chart)}')
                            await session.execute(text("""
                                INSERT INTO mapping_charts 
                                (mapping_id, chart_id, chart_type, chart_title, chart_config)
                                VALUES (:mapping_id, :chart_id, :chart_type, :chart_title, :chart_config)
                            """), {
                                "mapping_id": mapping.id,
                                "chart_id": chart_id,
                                "chart_type": chart.get('type'),
                                "chart_title": chart.get('title'),
                                "chart_config": json.dumps(chart) if isinstance(chart, dict) else str(chart)
                            })
                            charts_migrated += 1
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"  ⚠️  警告：Mapping {mapping.id} 的 charts 解析失败：{e}")
            
            print(f"  ✓ 迁移了 {charts_migrated} 个图表配置")
            
            # 4. 注意：SQLite 不支持 DROP COLUMN，需要重建表
            # 为了保持向后兼容，我们暂时保留旧字段
            print("[5/6] 保留旧 JSON 字段（向后兼容）...")
            print("  ℹ️  注意：SQLite 不支持 DROP COLUMN，旧字段将保留但不再使用")
            print("  ℹ️  应用层将通过 property 访问新数据")
            
            await session.commit()
            
            # 5. 验证迁移
            print("[6/6] 验证迁移结果...")
            
            # 验证 mapping_datasources
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mapping_datasources
            """))
            ds_count = result.scalar()
            
            # 验证 mapping_charts
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mapping_charts
            """))
            chart_count = result.scalar()
            
            # 验证 mappings 总数
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mappings
            """))
            mapping_count = result.scalar()
            
            print(f"\n迁移完成！")
            print(f"  ✓ Mappings 总数：{mapping_count}")
            print(f"  ✓ MappingDataSource 记录：{ds_count}")
            print(f"  ✓ MappingChart 记录：{chart_count}")
            
            # 检查是否有 mapping 没有数据源关联
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mappings m
                LEFT JOIN mapping_datasources md ON m.id = md.mapping_id
                WHERE md.mapping_id IS NULL
            """))
            orphan_count = result.scalar()
            
            if orphan_count > 0:
                print(f"  ⚠️  警告：{orphan_count} 个 mapping 没有数据源关联")
            
            print(f"\n[{datetime.now()}] 迁移成功完成！")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 迁移失败：{e}")
            import traceback
            traceback.print_exc()
            return False


async def migrate_downgrade():
    async with async_session() as session:
        try:
            # SQLite 不支持 DROP COLUMN，只能删除表
            print("[1/3] 删除 mapping_charts 表...")
            await session.execute(text("DROP TABLE IF EXISTS mapping_charts"))
            
            print("[2/3] 删除 mapping_datasources 表...")
            await session.execute(text("DROP TABLE IF EXISTS mapping_datasources"))
            
            await session.commit()
            
            print("[3/3] 回滚完成！")
            print("  ℹ️  旧 JSON 字段仍然保留在 mappings 表中")
            print(f"\n[{datetime.now()}] 回滚成功完成！")
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 回滚失败：{e}")
            import traceback
            traceback.print_exc()
            return False


# === 兼容函数别名（供外部调用）===

async def create_mapping_datasources_table():
    """创建 mapping_datasources 表"""
    async with async_session() as session:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS mapping_datasources (
                mapping_id INTEGER NOT NULL,
                datasource_id INTEGER NOT NULL,
                "order" INTEGER DEFAULT 0 NOT NULL,
                PRIMARY KEY (mapping_id, datasource_id),
                FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
                FOREIGN KEY (datasource_id) REFERENCES datasources(id) ON DELETE CASCADE
            )
        """))
        await session.commit()
        print("✓ mapping_datasources 表创建成功")


async def create_mapping_charts_table():
    """创建 mapping_charts 表"""
    async with async_session() as session:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS mapping_charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mapping_id INTEGER NOT NULL,
                chart_id VARCHAR(100) NOT NULL,
                chart_type VARCHAR(50),
                chart_title VARCHAR(255),
                chart_config JSON,
                FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
                UNIQUE (mapping_id, chart_id)
            )
        """))
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_mapping_charts_chart_id 
            ON mapping_charts(chart_id)
        """))
        await session.commit()
        print("✓ mapping_charts 表创建成功")


async def migrate_data():
    """迁移数据（migrate_upgrade 的别名）"""
    return await migrate_upgrade()


async def rollback():
    """回滚迁移（migrate_downgrade 的别名）"""
    return await migrate_downgrade()


# === 验证函数 ===

async def verify_migration():
    async with async_session() as session:
        try:
            # 1. 检查表是否存在
            print("[1/4] 检查表结构...")
            result = await session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('mapping_datasources', 'mapping_charts')
            """))
            tables = result.fetchall()
            
            if len(tables) != 2:
                print(f"  ❌ 表不完整：只找到 {len(tables)} 个表，需要 2 个")
                return False
            print("  ✓ 表结构正确")
            
            # 2. 检查外键约束
            print("[2/4] 检查外键约束...")
            result = await session.execute(text("PRAGMA foreign_keys"))
            fk_enabled = result.scalar()
            
            if not fk_enabled:
                print("  ⚠️  外键约束未启用")
            else:
                print("  ✓ 外键约束已启用")
            
            # 3. 检查数据完整性
            print("[3/4] 检查数据完整性...")
            
            # 检查孤立的 mapping_datasources
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mapping_datasources md
                LEFT JOIN mappings m ON md.mapping_id = m.id
                WHERE m.id IS NULL
            """))
            orphan_md = result.scalar()
            
            if orphan_md > 0:
                print(f"  ❌ 发现 {orphan_md} 条孤立的 mapping_datasources 记录")
                return False
            
            # 检查孤立的 mapping_charts
            result = await session.execute(text("""
                SELECT COUNT(*) FROM mapping_charts mc
                LEFT JOIN mappings m ON mc.mapping_id = m.id
                WHERE m.id IS NULL
            """))
            orphan_mc = result.scalar()
            
            if orphan_mc > 0:
                print(f"  ❌ 发现 {orphan_mc} 条孤立的 mapping_charts 记录")
                return False
            
            print("  ✓ 数据完整性正确")
            
            # 4. 测试查询
            print("[4/4] 测试查询...")
            
            # 测试查询 mapping 的数据源
            result = await session.execute(text("""
                SELECT m.id, m.name, GROUP_CONCAT(md.datasource_id) as ds_ids
                FROM mappings m
                LEFT JOIN mapping_datasources md ON m.id = md.mapping_id
                GROUP BY m.id
                LIMIT 1
            """))
            test_result = result.fetchone()
            
            if test_result:
                print(f"  ✓ 查询测试成功：Mapping {test_result[0]} ({test_result[1]})")
            else:
                print("  ℹ️  无 mapping 数据，跳过查询测试")
            
            print(f"\n[{datetime.now()}] 验证通过！")
            return True
            
        except Exception as e:
            print(f"\n❌ 验证失败：{e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    print("=" * 60)
    print("数据库迁移工具 v2.0")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python -m app.migrations.migrate_to_v2 upgrade    # 向上迁移")
        print("  python -m app.migrations.migrate_to_v2 downgrade  # 向下回滚")
        print("  python -m app.migrations.migrate_to_v2 verify     # 验证迁移")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'upgrade':
        success = await migrate_upgrade()
    elif command == 'downgrade':
        success = await migrate_downgrade()
    elif command == 'verify':
        success = await verify_migration()
    else:
        print(f"❌ 未知命令：{command}")
        print("可用命令：upgrade, downgrade, verify")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
