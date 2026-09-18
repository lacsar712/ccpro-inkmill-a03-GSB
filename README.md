# InkMill-01 · 油墨研磨台账

面向印刷油墨研磨车间的**研磨机状态、粘度取样与研磨遍次**台账系统。  
**不是**库存、电商或 CMS 场景。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11、Flask、SQLAlchemy、PyMySQL、Flask-JWT-Extended、passlib/bcrypt、gunicorn |
| 前端 | Svelte 4、Vite、TypeScript |
| 数据库 | MySQL 8 |

## 端口与数据库

| 服务 | 宿主机端口 |
|------|------------|
| 统一入口 (Nginx) | **4200** |
| 后端 API | **9200** |
| MySQL | **3312** |

MySQL 连接：`inkmill` / `inkmill` / `inkmill`（库名/用户/密码）

## 演示账号

密码均为 **123456**：

- `admin` — 管理员
- `grinder` — 研磨工

## 领域实体（JSON 驼峰）

1. **Workshop**：`name`, `site`, `notes`
2. **Mill**：`workshopId`, `millCode`（同车间唯一）, `pigmentBase`, `bowlLiters`, `status`（`grinding` \| `idle` \| `wash`）
3. **ViscositySample**：`millId`, `sampledAt`, `viscosityPaS`（须 &gt; 0，否则 HTTP 400）, `tempC`, `notes`
4. **GrindPass**：`millId`, `startedAt`, `passNo`（≥ 1）, `durationMin`（&gt; 0）, `mediaType`, `operatorName`
5. **ViscosityAlarmRule**（挂 Mill）：`millId`, `minPaS`, `maxPaS`（min 必须 &lt; max）, `active`
6. **ViscosityAlarmEvent**：`ruleId`, `sampleId`, `triggeredAt`, `level`（`warn` \| `critical`）, `message`, `acked`
7. **Dashboard**：`workshopTotal`, `grindingMillCount`, `samplesLast24h`, `passesLast7d`, `unackedAlarmCount`

### 粘度告警机制

- 规则挂在研磨机上，定义合格粘度区间 `[minPaS, maxPaS]`，仅 `active=true` 的规则参与判定。
- **新建** ViscositySample 后，后端自动查找该机台 active 规则：粘度落在区间外则为每条越界规则生成一条告警事件（取样接口响应本身仍返回取样记录）。
- 级别：越界量超过区间宽度一半（`超限 > (max-min)/2`）为 `critical`，否则为 `warn`；恰好等于半宽按 `warn` 计。
- 事件只能由后端判定生成，前端不做任何本地假告警。
- 种子数据含 1 条规则（M-01，10～14 Pa·s）与 3 条事件（1 条已确认、2 条未确认，涵盖 warn 与 critical）。

### 告警 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/viscosity-alarm-rules` | 规则列表（可带 `?millId=`）/ 新建规则 |
| PUT/DELETE | `/api/viscosity-alarm-rules/{id}` | 修改 / 删除规则（删除级联清理事件） |
| GET | `/api/viscosity-alarm-events` | 事件列表，可按 `?millId=`、`?acked=true\|false`、`?level=warn\|critical` 筛选 |
| POST | `/api/viscosity-alarm-events/{id}/ack` | 确认告警（幂等，置 `acked=true`） |

前端侧栏含「告警规则」「告警事件」两个入口；侧栏角标、仪表盘与粘度取样页均展示**未确认告警条数**（取自后端）。

## 快速启动（Docker）

```bash
cd InkMill-01
docker compose up --build -d
```

浏览器访问：**http://localhost:4200**  
前端 Nginx 将 `/api/` 反向代理到后端 `9200`。

后端容器启动流程：

1. 等待 MySQL 就绪（`DB_HOST=mysql`）
2. SQLAlchemy `create_all` 建表
3. `SEED_ON_START=true` 时写入演示数据
4. gunicorn 监听 `0.0.0.0:9200`

健康检查：`GET /api/health` → `{"status":"ok","service":"InkMill"}`

## 本地开发（可选）

**后端**（需本机 MySQL 或连 Docker 的 3312 端口）：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
set DB_HOST=127.0.0.1
set DB_PORT=3312
set DB_USER=inkmill
set DB_PASSWORD=inkmill
set DB_NAME=inkmill
set JWT_SECRET=inkmill-jwt-secret-change-me
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"
python -c "from app.seed import seed; seed()"
gunicorn wsgi:app --bind 127.0.0.1:9200 --reload
```

**前端**：

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器端口 **4200**，`/api` 代理到 `127.0.0.1:9200`。

## 目录结构

```
InkMill-01/
├── docker-compose.yml
├── nginx/nginx.conf          # 4200 统一入口，/api → backend
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── wsgi.py
│   └── app/                  # Flask 路由、模型、告警判定与种子数据
│       └── alarm_service.py  # 取样越界 → warn/critical 事件判定
└── frontend/
    ├── Dockerfile
    ├── vite.config.ts
    └── src/routes/           # Login / Dashboard / CRUD / 告警规则与事件页
```

## UI 主题

墨黑底 + 朱砂强调色，无紫色光晕风格。
