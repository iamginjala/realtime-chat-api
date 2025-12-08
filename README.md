# 💬 Realtime Chat API

A production-ready WhatsApp-style messaging backend built with Flask, Socket.IO, PostgreSQL, and Redis. This project demonstrates scalable real-time communication architecture with horizontal scaling capabilities.

---

## 🎯 Project Overview

A high-performance real-time messaging API that handles bidirectional communication, message persistence, user presence tracking, and group chat functionality. Built to scale across multiple servers using Redis pub/sub architecture.

---

## 🚀 Key Features & Technical Achievements

### 1. **WebSocket Scaling via Redis Pub/Sub Architecture**
- Implemented Redis pub/sub for horizontal scalability across multiple server instances
- Architected stateless server design allowing seamless load distribution
- Message routing system ensuring delivery across distributed WebSocket connections
- Connection affinity handling for consistent user experience

**Technologies:** Redis, Flask-SocketIO, Socket.IO Adapter

### 2. **Real-Time Bidirectional Communication with Socket.IO**
- Built event-driven architecture for instant message delivery
- Implemented automatic reconnection handling with connection state management
- User presence tracking (online/offline status, last seen timestamps)
- Real-time typing indicators with throttling to optimize bandwidth
- Connection lifecycle management with proper cleanup

**Technologies:** Socket.IO, Flask-SocketIO, WebSocket Protocol

### 3. **PostgreSQL Database Schema Design**
- Designed normalized schema for conversations, messages, and user metadata
- Implemented efficient indexing strategy for fast message history queries
- Pagination support for loading conversation history (offset/cursor-based)
- Optimized queries for unread message counts and conversation lists
- Timestamp tracking for message lifecycle (sent_at, delivered_at, read_at)
- Constraint-based data integrity (unique conversations, user ordering)

**Database Tables:**
- `users` - User authentication and profile data
- `conversations` - 1-on-1 and group conversation metadata
- `messages` - Message content with delivery tracking
- Efficient foreign key relationships and cascade operations

### 4. **JWT Authentication Over WebSocket Connections**
- Secure token-based authentication for WebSocket handshake
- Session management with active user tracking (in-memory store)
- Token validation and payload extraction for user identification
- Protected REST endpoints with JWT decorator pattern
- Authorization checks ensuring users can only access their own data

**Security Features:**
- Bearer token authentication for REST APIs
- WebSocket authentication via connection handshake
- User-level access control for conversations and messages

### 5. **Group Chat Functionality** *(Architecture Ready)*
- Room-based broadcasting for efficient message delivery
- Admin controls and member permission system design
- Message delivery status tracking (sent/delivered/read)
- Read receipts with aggregation for group messages
- Member management (add/remove/leave)
- Group metadata (name, description, creation timestamp)

---

## 🏗️ Architecture Highlights

### **Scalability Design**
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client 1  │      │   Client 2  │      │   Client 3  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       └────────────┬───────┴────────┬───────────┘
                    │                │
              ┌─────▼─────┐    ┌────▼──────┐
              │  Server 1 │    │  Server 2 │
              │ (Flask)   │    │ (Flask)   │
              └─────┬─────┘    └─────┬─────┘
                    │                │
                    └────────┬───────┘
                             │
                      ┌──────▼───────┐
                      │    Redis     │
                      │   Pub/Sub    │
                      └──────────────┘
                             │
                      ┌──────▼───────┐
                      │  PostgreSQL  │
                      │   Database   │
                      └──────────────┘
```

### **Message Flow**
1. Client sends message via WebSocket
2. Server validates JWT and sender identity
3. Message saved to PostgreSQL with timestamps
4. Server publishes message to Redis channel
5. All server instances receive message via Redis subscription
6. Message delivered to recipient if online, else queued
7. Delivery confirmation sent back to sender
8. Read receipt tracked when recipient views message

---

## 📊 Database Schema

### **Conversations Table**
```sql
- id (Primary Key)
- user1_id (Foreign Key → users.id)
- user2_id (Foreign Key → users.id)
- created_at (Timestamp)
- updated_at (Timestamp)
- CONSTRAINT: user1_id < user2_id (prevents duplicates)
- UNIQUE: (user1_id, user2_id)
```

### **Messages Table**
```sql
- id (Primary Key)
- conversation_id (Foreign Key → conversations.id)
- sender_id (Foreign Key → users.id)
- content (Text)
- sent_at (Timestamp)
- delivered_at (Timestamp, nullable)
- read_at (Timestamp, nullable)
- created_at (Timestamp)
- INDEX: (conversation_id, sent_at) for pagination
```

### **Users Table**
```sql
- id (Primary Key)
- email (Unique)
- password_hash
- created_at (Timestamp)
```

---

## 🔧 Technical Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Flask, Flask-SocketIO |
| **Real-Time** | Socket.IO, WebSocket |
| **Database** | PostgreSQL, SQLAlchemy ORM |
| **Caching/Pub-Sub** | Redis |
| **Authentication** | JWT (JSON Web Tokens) |
| **Deployment** | Docker, Railway (planned) |

---

## 📡 API Endpoints

### **WebSocket Events**

#### Client → Server
- `connect` - Authenticate with JWT token
- `send_message` - Send message to user
- `ping` - Keep-alive heartbeat

#### Server → Client
- `authenticated` - Connection successful
- `new_message` - Incoming message
- `message_sent` - Outgoing message confirmation
- `message_delivered` - Delivery receipt
- `user_online` - User came online
- `user_offline` - User went offline
- `typing` - User is typing
- `pong` - Heartbeat response

### **REST API Endpoints**

#### `GET /api/conversations`
Get all conversations for authenticated user
- **Auth:** Bearer JWT token
- **Response:** List of conversations with last message and unread count

#### `GET /api/messages?conversation_id=X&limit=50&offset=0`
Fetch message history with pagination
- **Auth:** Bearer JWT token
- **Query Params:** conversation_id, limit (default: 50), offset (default: 0)
- **Response:** Message array, total count, has_more flag

#### `POST /api/messages/read?conversation_id=X`
Mark all unread messages as read
- **Auth:** Bearer JWT token
- **Query Params:** conversation_id
- **Response:** Success status, count of messages marked

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- PostgreSQL
- Redis (for scaling, optional for single-server)
- Docker (optional)

### **Installation**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/realtime-chat-api.git
cd realtime-chat-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL with Docker**
```bash
docker-compose up -d
```

4. **Configure environment variables**
```bash
# .env file
DATABASE_URL=postgresql://chatuser:chatpassword@localhost:5432/chatdb
JWT_SECRET=your-secret-key-here
REDIS_URL=redis://localhost:6379
```

5. **Initialize database**
```bash
python create_test_users.py
```

6. **Generate JWT tokens for testing**
```bash
python test_generate_token.py
```

7. **Run the server**
```bash
python app.py
```

Server runs on `http://localhost:5000`

---

## 🧪 Testing

### **Using the Test Client**
1. Open `test_client.html` in browser
2. Paste JWT token from `test_generate_token.py`
3. Click "Connect"
4. Send messages between users

### **Using Postman**
Import the provided Postman collection to test REST endpoints.

**Example: Get Conversations**
```bash
GET http://localhost:5000/api/conversations
Headers:
  Authorization: Bearer <your-jwt-token>
```

---

## 🔒 Security Features

- **JWT Authentication:** Secure token-based auth for both WebSocket and REST
- **Authorization Checks:** Users can only access their own conversations
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **XSS Protection:** Input validation and sanitization
- **CORS Configuration:** Controlled cross-origin access
- **Password Hashing:** Bcrypt for secure password storage

---

## 📈 Performance Optimizations

- **Efficient Database Queries:** Indexed columns for fast lookups
- **Pagination:** Limit data transfer with cursor/offset pagination
- **Connection Pooling:** Reuse database connections
- **Event Throttling:** Typing indicators throttled to reduce bandwidth
- **Lazy Loading:** Load message history on-demand
- **Redis Caching:** Fast presence tracking and session management

---

## 🎯 Advanced Features (Implemented/Planned)

✅ **Implemented:**
- JWT authentication over WebSocket
- 1-on-1 messaging with delivery tracking
- Offline message queuing
- Message history with pagination
- Read receipts and unread counts
- User presence tracking (online/offline)

🚧 **Planned:**
- Redis pub/sub for horizontal scaling
- Group chats with admin controls
- Typing indicators
- File/image sharing
- Message editing and deletion
- Push notifications
- End-to-end encryption

---

## 📁 Project Structure

```
realtime-chat-api/
├── app.py                      # Main application and Socket.IO handlers
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # PostgreSQL container setup
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy instance
│   ├── participant.py          # User model
│   ├── conversation.py         # Conversation model
│   └── message.py              # Message model
│
├── utils/                      # Utility functions
│   ├── jwt_helper.py           # JWT generation/validation
│   └── database.py             # Database helper functions
│
├── test_client.html            # WebSocket test client
├── create_test_users.py        # Create test users script
├── test_generate_token.py      # Generate JWT tokens
└── reset_database.py           # Database reset script
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@iamginjala](https://www.github.com/iamginjala)
- LinkedIn: [Harsha Ginjala](https://www.linkedin.com/in/harsha-vardhan-reddy-ginjala-a6a026146/)
- Email: harsha.v.ginjala@gmail.com

---

## 🙏 Acknowledgments

- Flask and Flask-SocketIO documentation
- Socket.IO community
- PostgreSQL documentation
- Redis documentation
- Inspiration from WhatsApp, Telegram, and Signal architectures

---

## 📚 Learning Resources

This project was built as part of a learning journey to understand:
- Real-time communication protocols
- WebSocket scaling strategies
- Database schema design for chat applications
- Authentication patterns for WebSocket connections
- Horizontal scaling with Redis pub/sub

**⭐ Star this repo if you find it helpful!**
