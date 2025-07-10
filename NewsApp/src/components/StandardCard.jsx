import React from 'react';

const StandardCard = ({ item, index, expandedArticles, toggleArticleExpansion }) => (
  <div className="card bg-base-100 shadow-xl group hover:shadow-2xl transition-all duration-300 overflow-hidden relative">
    {item.image && (
      <div className="relative h-48 overflow-hidden">
        <img
          src={item.image}
          alt={item.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-2 left-2">
          {item.category && (
            <span className="badge badge-primary badge-lg shadow-md bg-opacity-90 backdrop-blur-sm">{item.category}</span>
          )}
        </div>
      </div>
    )}
    <div className="card-body">
      <h2 className="card-title text-lg font-bold leading-tight mb-1">{item.title}</h2>
      <p className="text-base-content/80 mb-2 line-clamp-3">{item.description}</p>
      <div className="flex items-center gap-2 mb-2">
        {item.bias_score !== undefined && (
          <span className="badge badge-info text-xs">Bias: {item.bias_score}</span>
        )}
        {item.bias_types && item.bias_types.length > 0 && (
          <span className="badge badge-warning text-xs">{item.bias_types.join(', ')}</span>
        )}
      </div>
      {item.full_text && (
        <div className="mt-2">
          <button
            onClick={() => toggleArticleExpansion(index)}
            className="btn btn-outline btn-primary btn-sm mb-2"
          >
            {expandedArticles.has(index) ? 'Hide Full Article' : 'Show Full Article'}
          </button>
          {expandedArticles.has(index) && (
            <div className="bg-base-200 p-4 rounded-lg mt-2 border max-h-64 overflow-y-auto">
              <div className="whitespace-pre-line leading-relaxed text-base-content text-sm">
                {item.full_text}
              </div>
            </div>
          )}
        </div>
      )}
      <div className="flex justify-between items-center mt-4 text-xs opacity-80">
        <div className="flex items-center gap-2">
          <div className="avatar">
            <div className="w-7 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
              <img src={`https://api.dicebear.com/7.x/identicon/svg?seed=${item.author || 'User'}`} alt="avatar" />
            </div>
          </div>
          <span>{item.author || (typeof item.source === 'object' ? item.source.name : (item.source || 'The Hindu'))}</span>
        </div>
        <span>{item.publishedAt ? new Date(item.publishedAt).toLocaleDateString() : ''}</span>
      </div>
    </div>
  </div>
);

export default StandardCard; 