<template>
  <div class="option-wrapper">
    <label :class="['option-button', { selected: isSelected }]">
      <input
        :type="inputType"
        :name="name"
        :value="option.id"
        :checked="isSelected"
        @change="onChange"
      />
      <span class="option-text">{{ option.text }}</span>
    </label>
  </div>
</template>

<script setup>
defineProps({
  option: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  inputType: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['change'])

const onChange = (event) => {
  emit('change', event.target.value, event.target.checked)
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins.scss';

.option-wrapper {
  @include base-container;
}

.option-button {
  @include base-container;
  display: flex;
  align-items: center;
  padding: clamp($spacing-sm, 2vw, $spacing-md);
  background: $background-light;
  border: 2px solid $border-light;
  border-radius: clamp($border-radius-sm, 2vw, $border-radius-md);
  cursor: pointer;
  transition: $transition-default;
  position: relative;
  overflow: hidden;

  @include hover-effect;

  &.selected {
    background: $selected-bg;
    border-color: $primary-color;
    color: $primary-dark;
    font-weight: 500;
  }

  input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }
}

.option-text {
  margin-left: $spacing-xs;
  @include responsive-text(0.9rem, 1.1rem);
  text-align: left;
  width: 100%;
  color: $text-secondary;
  padding-right: $spacing-xs;
}

.option-button.selected .option-text {
  color: $primary-dark;
}

@media (hover: none) {
  .option-button {
    @include touch-hover;
  }
}

@media (max-width: $breakpoint-mobile) {
  .option-button {
    padding: $spacing-sm $spacing-md;
  }
}
</style> 