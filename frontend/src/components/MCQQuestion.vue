<template>
  <BaseCard class="question-card">
    <h3 class="question-text">{{ question.text }}</h3>
    <div class="options-container">
      <MCQOption
        v-for="option in shuffledOptions"
        :key="option.id"
        :option="option"
        :is-selected="isSelected(option.id)"
        :input-type="question.allowMultiple ? 'checkbox' : 'radio'"
        :name="question.id"
        @change="onAnswerChange"
      />
    </div>
  </BaseCard>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits, computed } from 'vue'
import BaseCard from './common/BaseCard.vue'
import MCQOption from './MCQOption.vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  selectedAnswers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['answer-updated'])

// Function to shuffle array using Fisher-Yates algorithm
const shuffleArray = (array) => {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// Store shuffled options
const currentShuffleOrder = ref([])

// Compute shuffled options - pure computation
const shuffledOptions = computed(() => currentShuffleOrder.value)

// Watch for question changes and update shuffle order
watch(
  () => props.question,
  (newQuestion) => {
    if (newQuestion) {
      currentShuffleOrder.value = shuffleArray(newQuestion.options)
        .map(opt => ({ ...opt, questionId: newQuestion.id }))
    }
  },
  { immediate: true } // Run immediately on mount
)

const isSelected = (optionId) => {
  return props.selectedAnswers.includes(optionId)
}

const onAnswerChange = (optionId, isChecked) => {
  let newSelectedAnswers
  if (props.question.allowMultiple) {
    // For checkboxes
    if (isChecked) {
      newSelectedAnswers = [...props.selectedAnswers, optionId]
    } else {
      newSelectedAnswers = props.selectedAnswers.filter(id => id !== optionId)
    }
  } else {
    // For radio buttons
    newSelectedAnswers = [optionId]
  }
  emit('answer-updated', newSelectedAnswers)
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins.scss';

.question-card {
  max-width: 800px;
  margin: 0 auto;
  @include responsive-spacing($spacing-lg, $spacing-xl);
  background: var(--color-surface);
  box-shadow: 0 4px 6px var(--color-shadow);
}

.question-text {
  @include responsive-text(1.1rem, 1.4rem);
  color: var(--color-text);
  margin-bottom: clamp($spacing-md, 4vw, $spacing-xl);
  text-align: left;
  line-height: 1.5;
  font-weight: 600;
  padding-left: $spacing-xs;
}

.options-container {
  @include base-container;
  display: flex;
  flex-direction: column;
  gap: clamp($spacing-sm, 2vw, $spacing-md);
}

.option-button {
  background: var(--color-surface);
  border: 2px solid var(--color-border);

  &.selected {
    background: var(--color-selected);
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}

.option-text {
  color: var(--color-text-secondary);
}

@media (max-width: $breakpoint-tablet) {
  .question-card {
    border-radius: $border-radius-md;
    padding: clamp($spacing-md, 3vw, $spacing-lg);
  }
}

@media (max-width: $breakpoint-mobile) {
  .question-card {
    border-radius: $border-radius-sm;
    padding: $spacing-md;
  }

  .question-text {
    padding-left: 0;
    margin-bottom: $spacing-md;
  }

  .options-container {
    gap: $spacing-sm;
  }
}
</style>
