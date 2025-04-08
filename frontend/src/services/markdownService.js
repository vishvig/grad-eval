import axios from 'axios';

/**
 * Service for fetching markdown content
 */
export const markdownService = {
  /**
   * Fetches markdown content from a specified path
   * @param {string} path - Path to the markdown file
   * @returns {Promise<string>} - The markdown content
   */
  async getMarkdownContent(path) {
    try {
      const response = await axios.get(path);
      return response.data;
    } catch (error) {
      console.error('Error fetching markdown content:', error);
      throw error;
    }
  }
}; 