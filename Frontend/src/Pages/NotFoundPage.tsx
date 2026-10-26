import {useNavigate} from "react-router-dom";
export const NotFoundPage = () => {
    const navigate = useNavigate();
  return (
    <div>
        
        <p className="mt-4">The page you are looking for does not exist.</p>
        <button
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          onClick={() => navigate("/")}
        >
          Go Back to Home
        </button>
        
        
    </div>
  )
}
