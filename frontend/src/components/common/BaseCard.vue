<template>
  <div class="base-card">
    <slot></slot>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/mixins.scss';

.base-card {
  @include card;
}
</style> 