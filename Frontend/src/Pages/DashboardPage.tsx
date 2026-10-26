// Frontend/src/Pages/DashboardPage.tsx
import { UserButton } from '@clerk/react'
import { Link } from 'react-router-dom'

export const DashboardPage = () => {
  return (
    <div className="min-h-screen">
      <header className="flex justify-between items-center p-4 border-b">
        <Link to="/" className="text-blue-600 hover:underline">
          &larr; Back to Home
        </Link>
        <UserButton />
      </header>

      <main className="p-6">
        <h2 className="text-2xl font-bold">Welcome To DashboardPage</h2>
      </main>
    </div>
  )
}