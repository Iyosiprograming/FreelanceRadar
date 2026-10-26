// Frontend/src/Pages/HomePage.tsx
import { Show, SignInButton, SignUpButton, UserButton } from '@clerk/react'
import { Link } from 'react-router-dom'

export const HomePage = () => {
  return (
    <div className="p-4">
      <header className="flex justify-between items-center">
        <h1 className="text-xl font-bold">Welcome to the Home Page</h1>

        <nav>
          <Show when="signed-out">
            <SignInButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="mr-2 px-4 py-2 bg-blue-600 text-white rounded">Sign In</button>
            </SignInButton>
            <SignUpButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="px-4 py-2 border rounded">Sign Up</button>
            </SignUpButton>
          </Show>

          <Show when="signed-in">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="text-blue-600 hover:underline font-medium">
                Go to Dashboard
              </Link>
              <UserButton />
            </div>
          </Show>
        </nav>
      </header>
    </div>
  )
}