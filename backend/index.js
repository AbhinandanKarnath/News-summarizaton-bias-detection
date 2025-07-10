const axios = require('axios');

//https://newsapi.org/v2/everything?q=tesla&from=2025-06-07&sortBy=publishedAt&apiKey=ca39f7414d5e45f08eb7ca61f72422c0 api to use.

// const API_KEY = '0VmFbHG7SMUXUxF8GDEAERa1RQnuRXoSzhxRES0U'; // Replace this

const API_KEY = 'ca39f7414d5e45f08eb7ca61f72422c0'
const COUNTRY = 'in'; // India

const fetchIndianNews = async () => {
  try {
    const response = await axios.get(
      `https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=${API_KEY}`
    );

    const articles = response.data.data || response.data.articles;
    if (Array.isArray(articles)) {
      articles.forEach((article, index) => {
        console.log(`\n${index + 1}. ${article.title}\n${article.description}\nSource: ${article.source}\nURL: ${article.url}`);
      });
    } else {
      console.error('❌ Articles is not an array:', articles);
    }
  } catch (error) {
    console.error('❌ Error fetching news:', error.response?.data || error.message);
  }
};

fetchIndianNews();
