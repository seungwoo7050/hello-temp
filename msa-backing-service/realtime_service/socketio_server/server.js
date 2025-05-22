const { Server } = require("socket.io");
const { createAdapter } = require("@socket.io/redis-adapter");
const { createClient } = require("ioredis");
const { connect, StringCodec, Empty } = require("nats");
const PORT = process.env.PORT || 3000;
const NATS_URL = process.env.NATS_URL || "nats://localhost:4222";
const REDIS_HOST = process.env.REDIS_HOST || "localhost";
const REDIS_PORT = parseInt(process.env.REDIS_PORT || "6379");
const REDIS_PASSWORD = process.env.REDIS_PASSWORD;
const httpServer = require('http').createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Socket.IO Server is running...');
});

const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});
const pubClient = createClient({ host: REDIS_HOST, port: REDIS_PORT, password: REDIS_PASSWORD });
const subClient = pubClient.duplicate();

Promise.all([pubClient.connect(), subClient.connect()]).then(() => {
    io.adapter(createAdapter(pubClient, subClient));
    console.log("Socket.IO Redis adapter connected successfully.");
}).catch(err => {
    console.error("Failed to connect Socket.IO Redis adapter:", err);
});
const sc = StringCodec();
let natsConnection;

async function setupNats() {
  try {
    natsConnection = await connect({ servers: NATS_URL });
    console.log(`Connected to NATS server at ${natsConnection.getServer()}`);
    const subGlobalNotifications = natsConnection.subscribe("global.notifications");
    (async () => {
      for await (const msg of subGlobalNotifications) {
        const messageData = JSON.parse(sc.decode(msg.data));
        console.log(`Received NATS message on [${msg.subject}]:`, messageData);
        io.emit("notification", messageData);
      }
      console.log("Subscription [global.notifications] closed.");
    })();
   
    const subRoomServerMessages = natsConnection.subscribe("chat.room.*.server");
    (async () => {
        for await (const msg of subRoomServerMessages) {
            const parts = msg.subject.split('.');
            const roomId = parts[2];
            const messageData = JSON.parse(sc.decode(msg.data));
            console.log(`NATS to Room [${roomId}] on [${msg.subject}]:`, messageData);
            io.to(roomId).emit("room_message", { room: roomId, ...messageData });
        }
        console.log("Subscription [chat.room.*.server] closed.");
    })();


  } catch (err) {
    console.error(`Error connecting to NATS: ${err.message}`);
  }
}

setupNats();
io.on("connection", (socket) => {
  console.log(`Client connected: ${socket.id}`);
  socket.on("joinRoom", (roomName) => {
    socket.join(roomName);
    console.log(`Client ${socket.id} joined room: ${roomName}`);
    socket.emit("joinedRoom", `Successfully joined room: ${roomName}`);
    socket.to(roomName).emit("userJoined", { userId: socket.id, room: roomName });
  });

  socket.on("leaveRoom", (roomName) => {
    socket.leave(roomName);
    console.log(`Client ${socket.id} left room: ${roomName}`);
    socket.emit("leftRoom", `Successfully left room: ${roomName}`);
    socket.to(roomName).emit("userLeft", { userId: socket.id, room: roomName });
  });

  socket.on("chatMessage", (data) => {
    const { room, message } = data;
    console.log(`Message from ${socket.id} in room ${room}: ${message}`);
   
    io.to(room).emit("newMessage", { user: socket.id, room, message });

   
    if (natsConnection && room) {
      const natsSubject = `chat.room.${room}.client`;
      const payload = JSON.stringify({ userId: socket.id, message, timestamp: new Date() });
      natsConnection.publish(natsSubject, sc.encode(payload));
      console.log(`Published to NATS [${natsSubject}]: ${payload}`);
    }
  });

  socket.on("customEventFromClient", (data) => {
    console.log(`Custom event from ${socket.id}:`, data);
   
    if (natsConnection) {
        const natsSubject = `client.events.${socket.id}`;
        const payload = JSON.stringify({ eventName: "customEventFromClient", data, userId: socket.id });
        natsConnection.publish(natsSubject, sc.encode(payload));
        console.log(`Published client event to NATS [${natsSubject}]`);
    }
   
    socket.emit("eventAcknowledged", { status: "Received your custom event" });
  });

  socket.on("disconnect", (reason) => {
    console.log(`Client disconnected: ${socket.id}, reason: ${reason}`);
   
  });
});

httpServer.listen(PORT, () => {
  console.log(`Socket.IO server listening on port ${PORT}`);
});
process.on('SIGINT', async () => {
  console.log('SIGINT received. Shutting down gracefully...');
  io.close(async (err) => {
    if (err) {
      console.error('Error closing Socket.IO server:', err);
    } else {
      console.log('Socket.IO server closed.');
    }

    if (natsConnection) {
      console.log('Draining NATS connection...');
      await natsConnection.drain();
      console.log('NATS connection drained and closed.');
    }
    
    await Promise.all([
        pubClient.quit(),
        subClient.quit()
    ]);
    console.log('Redis connections closed.');

    httpServer.close(() => {
        console.log('HTTP server closed.');
        process.exit(0);
    });
  });
});