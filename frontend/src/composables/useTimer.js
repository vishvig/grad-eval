import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export const useTimer = () => {
  const router = useRouter()
  
  const SEVEN_DAYS_IN_MS = 7 * 24 * 60 * 60 * 1000 // 7 days in milliseconds
  const START_TIME_KEY = 'assessment_start_time'
  
  const startTime = ref(null)
  const timeLeft = ref(0)
  const timerPaused = ref(false)
  let timer = null

  const calculateTimeLeft = () => {
    const now = Date.now()
    const start = parseInt(localStorage.getItem(START_TIME_KEY))
    
    if (!start) {
      console.error('No start time found')
      return 0
    }

    const endTime = start + SEVEN_DAYS_IN_MS
    const remaining = Math.floor((endTime - now) / 1000) // Convert to seconds

    // If time has expired, redirect to expired page
    if (remaining <= 0) {
      router.push('/time-expired')
      return 0
    }

    return remaining
  }

  const formattedTime = computed(() => {
    const value = Math.max(timeLeft.value, 0) // Ensure non-negative value
    
    // Calculate days, hours, minutes, seconds
    const days = Math.floor(value / (24 * 60 * 60))
    const hours = Math.floor((value % (24 * 60 * 60)) / (60 * 60))
    const minutes = Math.floor((value % (60 * 60)) / 60)
    const seconds = value % 60
    
    // Format based on how much time is left
    let timeString
    if (days > 0) {
      timeString = `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      timeString = `${hours}h ${minutes}m ${seconds}s`
    } else {
      timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`
    }

    return `Time remaining: ${timeString}`
  })

  const initializeTimer = (initialEpoch = null) => {
    if (initialEpoch) {
      localStorage.setItem(START_TIME_KEY, initialEpoch.toString())
    }
    
    startTime.value = parseInt(localStorage.getItem(START_TIME_KEY))
    timeLeft.value = calculateTimeLeft()
  }

  const startTimer = () => {
    if (timer) clearInterval(timer)
    
    // Calculate initial time left
    timeLeft.value = calculateTimeLeft()
    
    timer = setInterval(() => {
      if (!timerPaused.value) {
        timeLeft.value = calculateTimeLeft()
      }
    }, 1000)
  }

  const pauseTimer = () => {
    timerPaused.value = true
  }

  const resumeTimer = () => {
    timerPaused.value = false
  }

  const stopTimer = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  const clearTimerData = () => {
    localStorage.removeItem(START_TIME_KEY)
  }

  // Cleanup on component unmount
  onUnmounted(() => {
    stopTimer()
  })

  return {
    timeLeft,
    formattedTime,
    timerPaused,
    startTime,
    initializeTimer,
    startTimer,
    pauseTimer,
    resumeTimer,
    stopTimer,
    clearTimerData
  }
} 