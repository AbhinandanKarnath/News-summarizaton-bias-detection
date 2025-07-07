const axios = require('axios');

const API_KEY = '0VmFbHG7SMUXUxF8GDEAERa1RQnuRXoSzhxRES0U'; // Replace this
const COUNTRY = 'in'; // India

const fetchIndianNews = async () => {
  try {
    const response = await axios.get(
      `https://api.thenewsapi.com/v1/news/all?api_token=${API_KEY}`
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
