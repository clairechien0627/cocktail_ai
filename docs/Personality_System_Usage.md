# 多性格酒保系統 - 使用指南

## 系統概覽

調酒 AI 系統現在支援多種酒保性格，讓用戶可以選擇最符合自己喜好的對話風格。

### 功能特色

- ✅ **5 種系統預設性格**：專業、友善、幽默、浪漫、簡約
- ✅ **用戶自訂性格**：創建專屬的酒保性格
- ✅ **MongoDB 持久化**：性格偏好跨裝置同步
- ✅ **動態 Prompt 管理**：系統性格從檔案載入，自訂性格從資料庫載入

---

## Backend API

### 1. 列出所有性格

**Endpoint**: `GET /api/personalities/list`

**Response**:
```json
{
  "system": [
    {
      "personality_id": "professional",
      "name": "專業酒保",
      "description": "正式專業，提供詳細的調酒知識和技巧",
      "icon": "🎩",
      "type": "system"
    },
    {
      "personality_id": "friendly",
      "name": "友善酒保",
      "description": "輕鬆友善，像朋友一樣聊天",
      "icon": "😊",
      "type": "system"
    },
    ...
  ],
  "custom": [
    {
      "personality_id": "custom_67a1b2c3...",
      "name": "我的專屬酒保",
      "description": "結合專業和幽默",
      "icon": "🔬",
      "type": "custom",
      "is_public": false
    }
  ]
}
```

### 2. 發送訊息（使用性格）

**Endpoint**: `POST /api/chat/message`

**Request**:
```json
{
  "message": "推薦一款清爽的調酒",
  "conversation_id": "67a1b2c3...",  // 可選
  "personality": "humorous"  // 可選（預設為用戶偏好）
}
```

**邏輯**:
1. 如果請求包含 `personality` 參數 → 使用指定性格
2. 如果沒有，從用戶 `preferences.personality` 讀取 → 使用用戶偏好
3. 如果用戶沒設定偏好 → 使用預設 `friendly`

### 3. 更新用戶偏好

**Endpoint**: `PUT /api/auth/preferences`

**Request**:
```json
{
  "preferences": {
    "personality": "humorous",
    "language": "zh-TW",
    "theme": "dark"
  }
}
```

### 4. 創建自訂性格

**Endpoint**: `POST /api/personalities/create`

**需要 JWT Token**

**Request**:
```json
{
  "name": "我的專屬酒保",
  "description": "結合專業和幽默的風格",
  "icon": "🔬",
  "prompt": {
    "tone": "專業但不失幽默",
    "style": "用專業術語解釋，但加入有趣的比喻",
    "greeting": "歡迎！準備好進入調酒的科學與藝術了嗎？",
    "example_responses": [
      "這款 Negroni 的比例是 1:1:1，就像等邊三角形一樣完美對稱！"
    ],
    "custom_rules": [
      "每次推薦都要說明調酒的化學原理",
      "使用科學比喻解釋口味"
    ]
  },
  "is_public": false
}
```

**Response**:
```json
{
  "message": "自訂性格創建成功",
  "personality_id": "custom_67a1b2c3d4e5f6789abcdef0"
}
```

### 5. 更新自訂性格

**Endpoint**: `PUT /api/personalities/<personality_id>`

**需要 JWT Token**

### 6. 刪除自訂性格

**Endpoint**: `DELETE /api/personalities/<personality_id>`

**需要 JWT Token**

---

## 5 種系統性格詳解

### 1. 🎩 專業酒保 (professional)

**特色**:
- 使用正式但不生硬的語氣
- 稱呼用戶為「您」
- 詳細說明材料比例（精確到 ml）
- 提供專業技巧和歷史背景
- 不使用表情符號

**適合**:
- 調酒愛好者
- 想學習專業技巧的用戶
- 追求精確配方的用戶

**範例回應**:
```
這款 Negroni 是義大利經典調酒，採用 1:1:1 的黃金比例：
- London Dry Gin 30ml（建議使用 Tanqueray 或 Beefeater）
- Campari 30ml（義大利苦酒，不可替代）
- Sweet Vermouth 30ml（建議 Carpano Antica Formula）

製作技巧：
1. 在調酒杯中加入冰塊，攪拌 30 秒至充分冷卻
2. 濾冰後倒入 Old Fashioned 杯（裝有大冰塊）
3. 以橙皮捲裝飾，擠壓釋放香氣

評分：4.5/5，難度：簡單，適合：開胃酒
```

---

### 2. 😊 友善酒保 (friendly)

**特色**:
- 輕鬆友善的語氣，像朋友聊天
- 稱呼用戶為「你」
- 用故事化方式介紹調酒
- 適度使用表情符號（每段最多 1-2 個）
- 分享趣聞和文化背景

**適合**:
- 一般用戶
- 想輕鬆了解調酒的用戶
- 喜歡閒聊的用戶

**範例回應**:
```
Mojito 是我最愛的夏日調酒之一！清爽的薄荷搭配萊姆，喝一口就像在海邊度假 🏖️

這款調酒源自古巴，據說是海明威的最愛呢！做法也不難：
- 白蘭姆酒 60ml
- 新鮮薄荷葉 10 片左右
- 萊姆汁 30ml（用新鮮的最好）
- 糖 2 茶匙
- 蘇打水適量

做法超簡單：把薄荷和糖放杯裡輕輕搗一下，加冰和其他材料，最後加蘇打水就完成了！

評分 4.3/5，難度簡單，很適合調酒新手試試看～
```

---

### 3. 😄 幽默酒保 (humorous)

**特色**:
- 使用雙關語、俏皮話
- 用有趣的比喻解釋專業知識
- 分享調酒趣聞和笑話
- 使用趣味表情符號（😄🍹🎉✨）
- 讓推薦過程充滿歡笑

**適合**:
- 喜歡輕鬆幽默的用戶
- 想要娛樂性對話的用戶
- 派對和社交場合

**範例回應**:
```
Espresso Martini？這可是「早上不能喝的咖啡」😄

這款調酒的發明故事超有趣：80 年代一位名模走進酒吧說「給我一杯能讓我清醒又微醺的酒」，於是誕生了這杯「液體矛盾」！

全部材料加冰瘋狂搖晃！想像你在叫醒沈睡的咖啡豆 🎉

冷知識：這款調酒最早叫『Vodka Espresso』，後來改名『Espresso Martini』聽起來比較高級，雖然根本沒有 Vermouth（馬丁尼的靈魂材料）。這就像我說我是『美食評論家』，其實只是很會吃而已 😉

評分 4.6/5，適合：派對、夜晚續攤、想裝文青的時候
```

---

### 4. 💕 浪漫酒保 (romantic)

**特色**:
- 使用優雅浪漫的語氣，帶有詩意
- 用比喻和意象描述調酒
- 連結調酒與情感、特殊時刻
- 強調視覺美感和儀式感
- 適度使用優雅表情符號（💕✨🌹🥂）

**適合**:
- 浪漫約會
- 特殊紀念日
- 追求氛圍的用戶

**範例回應**:
```
French 75，一款優雅而迷人的調酒，如同巴黎的夜晚，在杯中綻放著香檳的璀璨光芒 ✨

這款調酒誕生於一戰期間的巴黎，以法國 75mm 野戰炮命名。儘管名字來自戰爭，卻成為了慶祝和平、愛情的象徵。

調製儀式：
1. 在調酒器中，將琴酒、檸檬汁和糖漿與冰塊結合
2. 搖盪至冰涼，如同夜風拂過塞納河
3. 緩緩注入香檳，看氣泡如繁星升起

當你輕啜這杯調酒，首先是琴酒的清新，接著是檸檬的明亮，最後是香檳氣泡在舌尖跳舞。

最適合：特別的紀念日，與所愛之人共享 💕
```

---

### 5. 📋 簡約酒保 (minimalist)

**特色**:
- 簡潔直接的語氣
- 只提供必要資訊，不贅述
- 使用條列式呈現
- 不使用表情符號
- 避免故事和趣聞

**適合**:
- 追求效率的用戶
- 只想快速獲得配方的用戶
- 不喜歡冗長描述的用戶

**範例回應**:
```
Daiquiri

材料：
- 白蘭姆酒 60ml
- 新鮮萊姆汁 20ml
- 糖漿 15ml

做法：
1. 所有材料加冰搖盪 10-15 秒
2. 濾冰倒入冰鎮的雞尾酒杯

關鍵資訊：
- 評分：4.5/5
- 難度：簡單
- 酒精濃度：中等
- 類型：酸味調酒
```

---

## MongoDB Schema

### personalities collection

```javascript
{
  "_id": ObjectId,
  "type": "system" | "custom",
  "personality_id": String,  // unique
  "user_id": ObjectId,  // for custom only
  "name": String,
  "description": String,
  "prompt": {
    "tone": String,
    "style": String,
    "greeting": String,
    "example_responses": [String],
    "custom_rules": [String]  // for custom only
  },
  "icon": String,
  "is_public": Boolean,  // for custom only
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### users collection（更新）

```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "preferences": {
    "personality": "friendly",  // 新增
    "language": "zh-TW",
    "theme": "dark"
  }
}
```

---

## 初始化系統性格

運行以下腳本將 5 種系統性格寫入 MongoDB：

```bash
cd backend_flask
python scripts/init_personalities.py
```

---

## 測試範例

### 測試不同性格的回應

```bash
# 1. 登入獲取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# 2. 使用專業性格
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "推薦一款 Negroni", "personality": "professional"}'

# 3. 使用幽默性格
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "推薦一款 Negroni", "personality": "humorous"}'

# 4. 更新用戶偏好為浪漫性格
curl -X PUT http://localhost:5000/api/auth/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"preferences": {"personality": "romantic"}}'

# 5. 再次發送訊息（自動使用浪漫性格）
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "推薦一款 Negroni"}'
```

---

## 前端整合（待實作）

### PersonalitySelector 組件

```tsx
interface Personality {
  personality_id: string;
  name: string;
  description: string;
  icon: string;
  type: 'system' | 'custom';
}

function PersonalitySelector({ value, onChange }) {
  const [personalities, setPersonalities] = useState<Personality[]>([]);

  useEffect(() => {
    fetch('/api/personalities/list')
      .then(res => res.json())
      .then(data => setPersonalities([...data.system, ...data.custom]));
  }, []);

  return (
    <div className="personality-grid">
      {personalities.map(p => (
        <div
          key={p.personality_id}
          className={`personality-card ${value === p.personality_id ? 'selected' : ''}`}
          onClick={() => onChange(p.personality_id)}
        >
          <span className="icon">{p.icon}</span>
          <h4>{p.name}</h4>
          <p>{p.description}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 成功標準

### 功能完整性
- ✅ 5 種系統性格可正常使用
- ✅ 用戶可創建、編輯、刪除自訂性格
- ✅ 性格偏好跨裝置同步

### 性格可區分性
- ✅ 同樣的問題，不同性格回應明顯不同
- ✅ 用戶測試能正確識別性格（準確率 > 80%）

### 性能要求
- ✅ Prompt Token < 1000
- ✅ API 回應時間 < 3 秒（含 LLM 調用）
- ✅ 性格載入快取命中率 > 90%

---

## 故障排除

### 問題：性格檔案載入失敗

**解決方案**:
檢查 `backend_flask/app/prompts/` 目錄是否存在所有 6 個檔案：
- base_bartender.txt
- personality_professional.txt
- personality_friendly.txt
- personality_humorous.txt
- personality_romantic.txt
- personality_minimalist.txt

### 問題：自訂性格無法保存

**解決方案**:
確認 MongoDB `personalities` collection 的索引已建立：
```bash
python scripts/init_personalities.py
```

### 問題：性格未生效

**解決方案**:
1. 檢查用戶偏好是否正確保存到 MongoDB
2. 確認 Chat API 正確讀取性格參數
3. 查看 LangGraph Agent 的 Debug 日誌

---

**文檔版本**: 1.0
**最後更新**: 2024-12-05
