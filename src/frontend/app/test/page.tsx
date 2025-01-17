'use client';  // This is needed since we're using state/effects

import { useEffect, useState } from 'react'

export default function Home() {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/test/')
        const data = await response.json()
        setMessage(data.message)
      } catch (err) {
        setError('Failed to connect to the backend')
      }
    }

    testConnection()
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Testing Backend Connection</h1>
      {message && <p className="text-green-500">{message}</p>}
      {error && <p className="text-red-500">{error}</p>}
    </main>
  )
}