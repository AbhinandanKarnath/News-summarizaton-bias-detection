import React from 'react';

const InCard = ({ item, index, expandedArticles, toggleArticleExpansion }) => (
  <div className="card shadow-2xl hover:shadow-3xl transition-all duration-300 group overflow-hidden relative bg-base-100">
    {item.image && (
      <div className="absolute inset-0 z-0">
        <img
          src={item.image}
          alt={item.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300 opacity-80"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
      </div>
    )}
    <div className="card-body relative z-10 text-white">
      <div className="flex items-center gap-2 mb-2">
        {item.category && (
          <span className="badge badge-accent shadow-md bg-opacity-90 backdrop-blur-sm">{item.category}</span>
        )}
      </div>
      <h2 className="card-title text-xl font-bold leading-tight mb-1 drop-shadow-lg">{item.title}</h2>
      <p className="mb-2 opacity-90 line-clamp-3 drop-shadow-md">{item.description}</p>
      <div className="flex items-center gap-2 mb-2">
        {item.bias_score !== undefined && (
          <span className="badge badge-outline text-xs">Bias: {item.bias_score}</span>
        )}
      </div>
      {item.full_text && (
        <div className="mt-2">
          <button
            onClick={() => toggleArticleExpansion(index)}
            className="btn btn-outline btn-info btn-sm mb-2"
          >
            {expandedArticles.has(index) ? 'Hide Full Article' : 'Show Full Article'}
          </button>
          {expandedArticles.has(index) && (
            <div className="bg-white/20 p-4 rounded-lg mt-2 border max-h-64 overflow-y-auto">
              <div className="whitespace-pre-line leading-relaxed text-white text-sm">
                {item.full_text}
              </div>
            </div>
          )}
        </div>
      )}
      <div className="flex justify-between items-center mt-4 text-xs opacity-90">
        <div className="flex items-center gap-2">
          <div className="avatar">
            <div className="w-7 rounded-full ring ring-accent ring-offset-base-100 ring-offset-2">
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

export default InCard; 