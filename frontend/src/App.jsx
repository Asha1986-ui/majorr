import { BrowserRouter, Routes, Route } from "react-router-dom";

// Components & Guard
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";
import Chatbot from "./components/Chatbot/Chatbot";

// Pages
import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Assessment from "./pages/Assessment/Assessment";
import Result from "./pages/Result/Result";
import Dashboard from "./pages/Dashboard/Dashboard";
import About from "./pages/About/About";
import Contact from "./pages/Contact/Contact";
import DietPlan from "./pages/DietPlan/DietPlan";
import FoodAnalyzer from "./pages/FoodAnalyzer/FoodAnalyzer";
import Profile from "./pages/Profile/Profile";
import FindCare from "./pages/FindCare/FindCare";

function App() {
  return (
    <BrowserRouter>
      {/* Website-Wide Floating DiaSense AI Assistant Chatbot */}
      <Chatbot />

      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        {/* Protected User Routes (Require Login) */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assessment"
          element={
            <ProtectedRoute>
              <Assessment />
            </ProtectedRoute>
          }
        />
        <Route
          path="/result"
          element={
            <ProtectedRoute>
              <Result />
            </ProtectedRoute>
          }
        />
        <Route
          path="/diet-plan"
          element={
            <ProtectedRoute>
              <DietPlan />
            </ProtectedRoute>
          }
        />
        <Route
          path="/food-analyzer"
          element={
            <ProtectedRoute>
              <FoodAnalyzer />
            </ProtectedRoute>
          }
        />
        <Route
          path="/find-care"
          element={
            <ProtectedRoute>
              <FindCare />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;