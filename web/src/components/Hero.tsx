"use client";

import { useState } from 'react'
import { createBookmark } from '@/lib/api'

export default function Hero() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = await createBookmark(url)
      setResult(data)
      setError('')
    } catch (err) {
      setError('Failed to process bookmark')
      setResult(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight">
          BookmarkAI
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          AI-powered bookmark organization for knowledge workers
        </p>
      </div>

      <form onSubmit={handleSubmit} className="max-w-md mx-auto">
        <div className="space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
              Add Bookmark
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://example.com"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Add Bookmark
          </button>
        </div>
      </form>

      {result && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-medium text-lg mb-2">Summary</h3>
          <p className="text-gray-700 mb-4">{result.summary}</p>
          <div>
            <h4 className="font-medium mb-2">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {result.tags.map((tag: string, i: number) => (
                <span
                  key={i}
                  className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {error && <p className="text-red-500 text-center">{error}</p>}
    </div>
  )
}