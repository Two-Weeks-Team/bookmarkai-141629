"use client";

import { useState } from 'react'
import { getTags } from '@/lib/api'

export default function TagCloud({ text }: { text: string }) {
  const [tags, setTags] = useState<string[]>([])

  const handleGetTags = async () => {
    const data = await getTags(text)
    setTags(data.tags)
  }

  return (
    <div className="mt-6">
      <button
        onClick={handleGetTags}
        className="mb-4 px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
      >
        Generate Tags
      </button>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag, i) => (
          <span
            key={i}
            className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}