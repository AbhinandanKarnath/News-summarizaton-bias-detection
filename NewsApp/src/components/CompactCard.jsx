import React from 'react';

const CompactCard = ({ item, index, expandedArticles, toggleArticleExpansion }) => (
  <div className="card card-compact bg-base-100 shadow-lg hover:shadow-xl transition-shadow duration-300 flex flex-row overflow-hidden">
    {item.image && (
      <div className="relative w-28 h-28 flex-shrink-0 overflow-hidden">
        <img
          src={item.image}
          alt={item.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-2 left-2">
          {item.category && (
            <span className="badge badge-accent shadow-md bg-opacity-90 backdrop-blur-sm">{item.category}</span>
          )}
        </div>
      </div>
    )}
    <div className="card-body p-4 flex-1">
      <h3 className="font-semibold text-base leading-tight mb-1 line-clamp-2">{item.title}</h3>
      <p className="text-xs opacity-80 mb-2 line-clamp-2">{item.description?.substring(0, 100)}...</p>
      <div className="flex items-center gap-2 mb-1">
        {item.bias_score !== undefined && (
          <span className="badge badge-info text-xs">Bias: {item.bias_score}</span>
        )}
      </div>
      <div className="flex items-center gap-2 mt-2">
        <div className="avatar">
          <div className="w-6 rounded-full ring ring-accent ring-offset-base-100 ring-offset-2">
            <img src={`https://api.dicebear.com/7.x/identicon/svg?seed=${item.author || 'User'}`} alt="avatar" />
          </div>
        </div>
        <span className="text-xs opacity-70">{item.author} • {item.publishedAt ? new Date(item.publishedAt).toLocaleDateString() : ''}</span>
      </div>
      <div className="flex justify-end mt-2">
        <button
          onClick={() => toggleArticleExpansion(index)}
          className="btn btn-primary btn-xs"
        >
          {expandedArticles.has(index) ? 'Hide' : 'Read'}
        </button>
      </div>
      {expandedArticles.has(index) && (
        <div className="mt-3 p-3 bg-base-200 rounded-lg">
          <p className="text-xs leading-relaxed">{item.full_text}</p>
        </div>
      )}
    </div>
  </div>
);

export default CompactCard; 