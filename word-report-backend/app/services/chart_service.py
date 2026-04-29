import os
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator
import matplotlib.dates as mdates
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO
from app.core.config import settings
from app.services.storage_service import storage_service

rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


class ChartColor:
    COLORS = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc',
    ]
    
    @staticmethod
    def get_color(index: int) -> str:
        return ChartColor.COLORS[index % len(ChartColor.COLORS)]
    
    @staticmethod
    def get_color_scheme(name: str) -> List[str]:
        schemes = {
            'default': ChartColor.COLORS,
            'blue': ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78'],
            'green': ['#2ca02c', '#98df8a', '#1f77b4', '#aec7e8'],
        }
        return schemes.get(name, schemes['default'])


class ChartService:
    def __init__(self):
        self.storage_prefix = "charts"
        self.dpi = settings.CHART_DPI
        self.chart_path = settings.CHART_STORAGE_PATH
    
    def generate_single_chart(self, chart_data: dict) -> dict:
        chart_type = chart_data.get('type', 'bar')
        
        if chart_type == 'settlement_duration':
            return self.generate_settlement_duration_curve(chart_data)
        elif chart_type == 'waterlevel_duration':
            return self.generate_water_level_duration_curve(chart_data)
        elif chart_type == 'settlement_waterlevel_comparison':
            return self.generate_layer_settlement_waterlevel_comparison(chart_data)
        
        try:
            chart_type = chart_data.get('type', 'bar')
            title = chart_data.get('title', '')
            x_label = chart_data.get('x_label', '')
            y_label = chart_data.get('y_label', '')
            x_data = chart_data.get('x_data', [])
            y_data = chart_data.get('y_data', [])
            color_scheme = chart_data.get('color_scheme', 'default')
            
            colors = ChartColor.get_color_scheme(color_scheme)
            
            plt.close('all')
            plt.clf()
            plt.cla()
            
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            ax.set_facecolor('white')
            
            y_numeric = [float(y) for y in y_data]
            
            if chart_type == 'bar':
                x_pos = list(range(len(x_data)))
                bars = ax.bar(x_pos, y_numeric, color=colors[0], width=0.6)
                
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{height:.0f}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 3),
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=10)
                
                ax.set_xticks(x_pos)
                ax.set_xticklabels(x_data)
                
            elif chart_type == 'line':
                ax.plot(range(len(x_data)), y_numeric, marker='o', 
                       linewidth=2, color=colors[0], markersize=8)
                ax.set_xticks(range(len(x_data)))
                ax.set_xticklabels(x_data)
                
            elif chart_type == 'combo':
                x_pos = list(range(len(x_data)))
                ax.bar(x_pos, y_numeric, color=colors[0], width=0.4, label='Data')
                ax2 = ax.twinx()
                ax2.plot(x_pos, y_numeric, marker='o', linewidth=2, color=colors[1], label='Trend')
                ax.set_xticks(x_pos)
                ax.set_xticklabels(x_data)
                ax.legend(loc='upper left')
                ax2.legend(loc='upper right')
            
            elif chart_type == 'pie':
                wedges, texts, autotexts = ax.pie(
                    y_numeric, 
                    labels=x_data,
                    autopct='%1.1f%%',
                    colors=colors[:len(y_numeric)],
                    startangle=90
                )
                for autotext in autotexts:
                    autotext.set_fontsize(10)
                    autotext.set_fontweight('bold')
                ax.set_title(title, fontsize=14, pad=10)
            
            ax.set_title(title, fontsize=14, pad=10)
            ax.set_xlabel(x_label, fontsize=11)
            ax.set_ylabel(y_label, fontsize=11)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            plt.tight_layout()
            
            unique_id = chart_data.get('id') or uuid.uuid4().hex[:12]
            filename = f"chart_{unique_id}.png"
            
            buf = BytesIO()
            fig.savefig(buf, dpi=self.dpi, format='png')
            buf.seek(0)
            file_data = buf.getvalue()
            buf.close()
            plt.close(fig)
            
            local_path = os.path.join(self.chart_path, filename)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            object_name = f"{self.storage_prefix}/{filename}"
            buf = BytesIO(file_data)
            storage_service.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                buf,
                length=len(file_data),
                content_type='image/png'
            )
            
            file_size = len(file_data)
            url = f"/api/charts/{filename}"
            
            return {
                "id": unique_id,
                "filename": filename,
                "filepath": local_path,
                "file_size": file_size,
                "url": url
            }
        except Exception as e:
            return {
                "error": str(e),
                "chart_data": chart_data.get('title', 'Unknown')
            }

    def generate_settlement_duration_curve(self, chart_data: dict) -> dict:
        try:
            chart_type = chart_data.get('subtype', 'long')
            title = chart_data.get('title', '地面沉降历时曲线')
            station_name = chart_data.get('station_name', '')
            
            x_data = chart_data.get('x_data', [])
            y_data = chart_data.get('y_data', [])
            
            dates = []
            values = []
            for i, date_str in enumerate(x_data):
                try:
                    for fmt in ['%Y-%m', '%Y-%m-%d', '%Y/%m', '%Y年%m月']:
                        try:
                            dt = datetime.strptime(str(date_str), fmt)
                            dates.append(dt)
                            break
                        except:
                            continue
                    else:
                        continue
                    
                    val = float(y_data[i]) if i < len(y_data) else 0
                    values.append(val)
                except:
                    continue
            
            if not dates:
                raise ValueError("无效的日期数据")
            
            plt.close('all')
            fig, ax = plt.subplots(figsize=(14, 7), dpi=100)
            ax.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('white')
            
            ax.plot(dates, values, marker='o', linewidth=2.5, markersize=6, 
                   color='#dc3545', label='累计沉降量', markerfacecolor='white', 
                   markeredgecolor='#dc3545', markeredgewidth=2)
            
            ax.fill_between(dates, values, 0, alpha=0.15, color='#dc3545')
            
            if chart_type == 'long':
                ax.xaxis.set_major_locator(YearLocator(2))
                ax.xaxis.set_major_formatter(DateFormatter('%Y'))
            else:
                ax.xaxis.set_major_locator(MonthLocator(interval=2))
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
            
            ax.xaxis.set_minor_locator(MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)
            
            ax.axhline(y=0, color='#6c757d', linestyle='--', linewidth=1.2)
            
            full_title = f"{station_name}\n{title}" if station_name else title
            ax.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color='#212529')
            ax.set_xlabel('日期', fontsize=12, fontweight='bold', color='#212529')
            ax.set_ylabel('累计沉降量 (mm)', fontsize=12, fontweight='bold', color='#212529')
            
            ax.yaxis.set_major_locator(plt.MultipleLocator(max(abs(max(values)-min(values))/5, 1)))
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#dee2e6')
            ax.spines['bottom'].set_color('#dee2e6')
            ax.grid(axis='y', linestyle='--', alpha=0.5, color='#dee2e6')
            ax.grid(axis='x', linestyle='--', alpha=0.3, color='#dee2e6')
            
            ax.tick_params(axis='y', colors='#495057')
            ax.tick_params(axis='x', colors='#495057')
            
            plt.tight_layout()
            
            unique_id = chart_data.get('id') or uuid.uuid4().hex[:12]
            filename = f"settlement_{unique_id}.png"
            
            buf = BytesIO()
            fig.savefig(buf, dpi=self.dpi, format='png')
            buf.seek(0)
            file_data = buf.getvalue()
            buf.close()
            plt.close(fig)
            
            local_path = os.path.join(self.chart_path, filename)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            object_name = f"{self.storage_prefix}/{filename}"
            buf = BytesIO(file_data)
            storage_service.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                buf,
                length=len(file_data),
                content_type='image/png'
            )
            
            return {
                "id": unique_id,
                "filename": filename,
                "filepath": local_path,
                "file_size": len(file_data),
                "url": f"/api/charts/{filename}"
            }
        except Exception as e:
            return {"error": str(e), "chart_data": chart_data.get('title', 'Settlement')}

    def generate_water_level_duration_curve(self, chart_data: dict) -> dict:
        try:
            title = chart_data.get('title', '地下水位历时曲线')
            station_name = chart_data.get('station_name', '')
            
            layers_data = chart_data.get('layers', {})
            
            if not layers_data:
                raise ValueError("缺少含水层数据")
            
            plt.close('all')
            fig, ax = plt.subplots(figsize=(16, 8), dpi=100)
            ax.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('white')
            
            colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#17a2b8']
            layer_names = list(layers_data.keys())
            
            all_dates = []
            for layer_name, data in layers_data.items():
                dates = data.get('dates', [])
                for d in dates:
                    try:
                        for fmt in ['%Y-%m', '%Y-%m-%d', '%Y/%m']:
                            try:
                                dt = datetime.strptime(str(d), fmt)
                                all_dates.append(dt)
                                break
                            except:
                                continue
                    except:
                        continue
            
            if not all_dates:
                raise ValueError("无效的日期数据")
            
            min_date = min(all_dates)
            max_date = max(all_dates)
            
            for idx, (layer_name, data) in enumerate(layers_data.items()):
                dates = []
                values = []
                
                for i, date_str in enumerate(data.get('dates', [])):
                    try:
                        for fmt in ['%Y-%m', '%Y-%m-%d', '%Y/%m']:
                            try:
                                dt = datetime.strptime(str(date_str), fmt)
                                dates.append(dt)
                                break
                            except:
                                continue
                    except:
                        continue
                
                vals = data.get('values', [])
                values = [float(v) for v in vals[:len(dates)] if v is not None]
                
                min_len = min(len(dates), len(values))
                dates = dates[:min_len]
                values = values[:min_len]
                
                if dates and values:
                    ax.plot(dates, values, marker='o', linewidth=2.5, markersize=5,
                           color=colors[idx % len(colors)], label=layer_name,
                           markerfacecolor='white', markeredgewidth=1.5)
            
            date_range = (max_date - min_date).days
            if date_range > 365 * 3:
                ax.xaxis.set_major_locator(YearLocator(1))
                ax.xaxis.set_major_formatter(DateFormatter('%Y'))
            elif date_range > 180:
                ax.xaxis.set_major_locator(MonthLocator(interval=3))
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
            else:
                ax.xaxis.set_major_locator(MonthLocator())
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)
            
            full_title = f"{station_name}\n{title}" if station_name else title
            ax.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color='#212529')
            ax.set_xlabel('日期', fontsize=12, fontweight='bold', color='#212529')
            ax.set_ylabel('水位标高 (m)', fontsize=12, fontweight='bold', color='#212529')
            
            ax.legend(loc='upper right', fontsize=10, framealpha=0.9, 
                     facecolor='white', edgecolor='#dee2e6')
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#dee2e6')
            ax.spines['bottom'].set_color('#dee2e6')
            ax.grid(axis='y', linestyle='--', alpha=0.5, color='#dee2e6')
            ax.grid(axis='x', linestyle='--', alpha=0.3, color='#dee2e6')
            
            ax.tick_params(axis='y', colors='#495057')
            ax.tick_params(axis='x', colors='#495057')
            
            plt.tight_layout()
            
            unique_id = chart_data.get('id') or uuid.uuid4().hex[:12]
            filename = f"waterlevel_{unique_id}.png"
            ax.set_ylabel('水位标高 (m)', fontsize=11)
            
            ax.legend(loc='upper right', fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            ax.grid(axis='x', linestyle='--', alpha=0.3)
            
            plt.tight_layout()
            
            unique_id = chart_data.get('id') or uuid.uuid4().hex[:12]
            filename = f"waterlevel_{unique_id}.png"
            
            buf = BytesIO()
            fig.savefig(buf, dpi=self.dpi, format='png')
            buf.seek(0)
            file_data = buf.getvalue()
            buf.close()
            plt.close(fig)
            
            local_path = os.path.join(self.chart_path, filename)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            object_name = f"{self.storage_prefix}/{filename}"
            buf = BytesIO(file_data)
            storage_service.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                buf,
                length=len(file_data),
                content_type='image/png'
            )
            
            return {
                "id": unique_id,
                "filename": filename,
                "filepath": local_path,
                "file_size": len(file_data),
                "url": f"/api/charts/{filename}"
            }
        except Exception as e:
            return {"error": str(e), "chart_data": chart_data.get('title', 'WaterLevel')}

    def generate_layer_settlement_waterlevel_comparison(self, chart_data: dict) -> dict:
        try:
            title = chart_data.get('title', '分层标与地下水位对比')
            station_name = chart_data.get('station_name', '')
            
            settlement_data = chart_data.get('settlement', {})
            waterlevel_data = chart_data.get('waterlevel', {})
            
            plt.close('all')
            fig, ax1 = plt.subplots(figsize=(16, 8), dpi=100)
            ax1.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('white')
            
            colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1']
            
            settlement_dates = settlement_data.get('dates', [])
            settlement_layers = settlement_data.get('layers', {})
            
            valid_dates = []
            for d in settlement_dates:
                try:
                    for fmt in ['%Y-%m', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(str(d), fmt)
                            valid_dates.append(dt)
                            break
                        except:
                            continue
                except:
                    continue
            
            if valid_dates:
                ax1.set_xlabel('日期', fontsize=12, fontweight='bold', color='#212529')
                ax1.set_ylabel('累计沉降量 (mm)', fontsize=12, fontweight='bold', color='#dc3545')
                
                for idx, (layer_name, values) in enumerate(settlement_layers.items()):
                    vals = [float(v) for v in values[:len(valid_dates)] if v is not None]
                    min_len = min(len(valid_dates), len(vals))
                    if min_len > 0:
                        ax1.plot(valid_dates[:min_len], vals[:min_len], 
                                marker='o', linewidth=2.5, markersize=5,
                                color='#dc3545', label=f'{layer_name}',
                                markerfacecolor='white', markeredgewidth=1.5)
                
                ax1.tick_params(axis='y', labelcolor='#dc3545', colors='#dc3545')
                ax1.yaxis.set_major_locator(plt.MultipleLocator(2))
            
            ax2 = ax1.twinx()
            waterlevel_dates = waterlevel_data.get('dates', [])
            waterlevel_layers = waterlevel_data.get('layers', {})
            
            wl_dates = []
            for d in waterlevel_dates:
                try:
                    for fmt in ['%Y-%m', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(str(d), fmt)
                            wl_dates.append(dt)
                            break
                        except:
                            continue
                except:
                    continue
            
            if wl_dates:
                ax2.set_ylabel('地下水位标高 (m)', fontsize=12, fontweight='bold', color='#007bff')
                
                for idx, (layer_name, values) in enumerate(waterlevel_layers.items()):
                    vals = [float(v) for v in values[:len(wl_dates)] if v is not None]
                    min_len = min(len(wl_dates), len(vals))
                    if min_len > 0:
                        ax2.plot(wl_dates[:min_len], vals[:min_len],
                                marker='s', linewidth=2.5, markersize=5,
                                color=colors[idx % len(colors)], label=f'{layer_name}',
                                markerfacecolor='white', markeredgewidth=1.5)
                
                ax2.tick_params(axis='y', labelcolor='#007bff', colors='#007bff')
                ax2.yaxis.set_major_locator(plt.MultipleLocator(1))
            
            all_dates = valid_dates + wl_dates
            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)
                date_range = (max_date - min_date).days
                
                if date_range > 365 * 2:
                    ax1.xaxis.set_major_locator(YearLocator(1))
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y'))
                elif date_range > 180:
                    ax1.xaxis.set_major_locator(MonthLocator(interval=3))
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                else:
                    ax1.xaxis.set_major_locator(MonthLocator())
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)
            
            full_title = f"{station_name}\n{title}" if station_name else title
            ax1.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color='#212529')
            
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10,
                      framealpha=0.9, facecolor='white', edgecolor='#dee2e6')
            
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.spines['left'].set_color('#dee2e6')
            ax1.spines['bottom'].set_color('#dee2e6')
            ax1.grid(axis='y', linestyle='--', alpha=0.5, color='#dee2e6')
            
            ax1.tick_params(axis='y', colors='#495057')
            ax1.tick_params(axis='x', colors='#495057')
            
            plt.tight_layout()
            
            unique_id = chart_data.get('id') or uuid.uuid4().hex[:12]
            filename = f"comparison_{unique_id}.png"
            
            buf = BytesIO()
            fig.savefig(buf, dpi=self.dpi, format='png')
            buf.seek(0)
            file_data = buf.getvalue()
            buf.close()
            plt.close(fig)
            
            local_path = os.path.join(self.chart_path, filename)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            
            object_name = f"{self.storage_prefix}/{filename}"
            buf = BytesIO(file_data)
            storage_service.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                buf,
                length=len(file_data),
                content_type='image/png'
            )
            
            return {
                "id": unique_id,
                "filename": filename,
                "filepath": local_path,
                "file_size": len(file_data),
                "url": f"/api/charts/{filename}"
            }
        except Exception as e:
            return {"error": str(e), "chart_data": chart_data.get('title', 'Comparison')}
    
    def generate_charts(self, charts: List[dict]) -> List[dict]:
        results = []
        for chart_data in charts:
            result = self.generate_single_chart(chart_data)
            results.append(result)
        return results
    
    async def get_chart_file(self, filename: str) -> Optional[bytes]:
        object_name = f"{self.storage_prefix}/{filename}"
        try:
            data = await storage_service.download_file(object_name)
            return data
        except:
            return None
    
    async def delete_chart(self, filename: str) -> bool:
        object_name = f"{self.storage_prefix}/{filename}"
        try:
            await storage_service.delete_file(object_name)
            return True
        except:
            return False
    
    async def list_charts(self) -> List[dict]:
        try:
            from minio import Minio
            client = storage_service.client
            objects = list(client.list_objects(settings.MINIO_BUCKET, prefix=f"{self.storage_prefix}/"))
            charts = []
            for obj in objects:
                charts.append({
                    "filename": obj.object_name.replace(f"{self.storage_prefix}/", ""),
                    "file_size": obj.size,
                    "create_time": obj.last_modified.strftime("%Y-%m-%d %H:%M:%S") if obj.last_modified else ""
                })
            return charts
        except:
            return []


chart_service = ChartService()