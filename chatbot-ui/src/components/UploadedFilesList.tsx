import React from 'react'

interface UploadedFilesListProps {
  files: File[]
  onClear: () => void
}

const UploadedFilesList: React.FC<UploadedFilesListProps> = ({ files, onClear }) => {
  if (!files || files.length === 0) return null

  return (
    <div className="uploaded-files" data-testid="uploaded-files" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span>Attached:</span>
      <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', gap: 8 }}>
        {files.map((f, idx) => (
          <li key={`${f.name}-${idx}`} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: 4 }}>
            {f.name}
          </li>
        ))}
      </ul>
      <button type="button" onClick={onClear} className="clear-files" data-testid="clear-files-button"
        style={{ border: '1px solid #888', padding: '4px 8px', borderRadius: 4, background: '#f5f5f5', cursor: 'pointer' }}>
        Clear
      </button>
    </div>
  )
}

export default UploadedFilesList
