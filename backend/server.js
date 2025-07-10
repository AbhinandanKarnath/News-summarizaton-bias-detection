import express from 'express';
import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import cors from 'cors';

const JWT_SECRET = 'your_jwt_secret'; // Change this in production
const MONGO_URI = 'mongodb://localhost:27017/newsapp';

// Mongoose models
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  passwordHash: { type: String, required: true },
  username: { type: String, required: true }
});
const User = mongoose.model('User', userSchema);

const articleHistorySchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  articleId: String,
  title: String,
  readAt: { type: Date, default: Date.now },
  meta: Object
});
const ArticleHistory = mongoose.model('ArticleHistory', articleHistorySchema);

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error('MongoDB connection error:', err));

// Signup
app.post('/api/signup', async (req, res) => {
  const { email, password, username } = req.body;
  if (!email || !password || !username) return res.status(400).json({ error: 'Missing fields' });
  const existing = await User.findOne({ email });
  if (existing) return res.status(409).json({ error: 'Email already registered' });
  const passwordHash = await bcrypt.hash(password, 10);
  const user = new User({ email, passwordHash, username });
  await user.save();
  res.json({ message: 'Signup successful' });
});

// Login
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });
  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) return res.status(401).json({ error: 'Invalid credentials' });
  const token = jwt.sign({ userId: user._id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, username: user.username, email: user.email });
});

// Auth middleware
function auth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: 'No token' });
  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

// Save article to history
app.post('/api/history', auth, async (req, res) => {
  const { articleId, title, meta } = req.body;
  const entry = new ArticleHistory({
    userId: req.user.userId,
    articleId,
    title,
    meta
  });
  await entry.save();
  res.json({ message: 'History saved' });
});

// Get user's article history
app.get('/api/history', auth, async (req, res) => {
  const history = await ArticleHistory.find({ userId: req.user.userId }).sort({ readAt: -1 });
  res.json({ history });
});

// Health check
app.get('/', (req, res) => res.send('API running'));

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log('Server running on port', PORT)); 