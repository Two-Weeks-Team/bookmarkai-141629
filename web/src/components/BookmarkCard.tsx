"use client";

import { useState } from 'react'
import { getSummary } from '@/lib/api'

export default function BookmarkCard({ url }: { url: string }) {
  const [summary, setSummary] = useState('')
  const [expanded, setExpanded] = useState(false)

  const handleExpand = async () => {
    if (!summary) {
      const data = await getSummary(url)
      setSummary(data.summary)
    }
    setExpanded(!expanded)
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
      <div className="flex justify-between items-start">
        <h3 className="font-medium text-lg truncate">{url}</h3>
        <button
          onClick={handleExpand}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {expanded ? 'Show summary' : 'Expand'}
        </button>
      </div>
      {summary && (
        <div className="mt-2">
          <p className={expanded ? '' : 'line-clamp-1'}>
            {summary}
          </p>
        </div>
      )}
    </div>
  )
}