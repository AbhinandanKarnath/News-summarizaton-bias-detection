import React from 'react';

const ListCard = ({ item, index, expandedArticles, toggleArticleExpansion }) => (
  <div className="bg-base-100 shadow-md hover:shadow-lg transition-shadow duration-300 rounded-lg p-4 border border-base-300 flex gap-4 items-start overflow-hidden">
    {item.image && (
      <img
        src={item.image}
        alt={item.title}
        className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
      />
    )}
    <div className="flex-1">
      <div className="flex items-center gap-2 mb-2">
        {item.category && (
          <span className="badge badge-warning shadow-md">{item.category}</span>
        )}
      </div>
      <h3 className="font-bold text-lg mb-2 line-clamp-2">{item.title}</h3>
      <p className="text-sm text-base-content/80 mb-3 line-clamp-3">{item.description}</p>
      <div className="flex items-center gap-2 mb-2">
        {item.bias_score !== undefined && (
          <span className="badge badge-info text-xs">Bias: {item.bias_score}</span>
        )}
      </div>
      <div className="flex items-center gap-2 mt-2">
        <div className="avatar">
          <div className="w-6 rounded-full ring ring-warning ring-offset-base-100 ring-offset-2">
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
          {expandedArticles.has(index) ? 'Hide Details' : 'Read More'}
        </button>
      </div>
      {expandedArticles.has(index) && (
        <div className="mt-4 p-4 bg-base-200 rounded-lg border-l-4 border-primary">
          <p className="text-sm leading-relaxed">{item.full_text}</p>
        </div>
      )}
    </div>
  </div>
);

export default ListCard; 