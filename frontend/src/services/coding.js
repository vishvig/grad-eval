import axios from 'axios'
import { CODING } from '@/constants/api'

export default {
  async downloadTaskFiles(params) {
    const response = await axios.post(CODING.DOWNLOAD_TASK_FILES, params, {
      responseType: 'blob'
    })
    return response.data
  }
} 