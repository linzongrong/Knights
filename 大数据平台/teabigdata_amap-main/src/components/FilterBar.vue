<template>
  <div class="filter-bar card">
    <div class="filter-group">
      <label>{{ t('filter.nameLabel') }}</label>
      <input type="text" v-model="name" :placeholder="t('filter.namePlaceholder')" @input="updateFilter" />
    </div>
    <div class="filter-group">
      <label>{{ t('filter.dbhLabel') }}</label>
      <input type="number" v-model.number="minDbh" :placeholder="t('filter.minPlaceholder')" @input="updateFilter" class="input-short" />
      <span>-</span>
      <input type="number" v-model.number="maxDbh" :placeholder="t('filter.maxPlaceholder')" @input="updateFilter" class="input-short" />
    </div>
    <button @click="confirm" class="btn-confirm">{{ t('filter.confirm') }}</button>
    <button @click="resetFilter" class="btn-reset">{{ t('filter.reset') }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from '../composables/useI18n';

const { t } = useI18n();

const emit = defineEmits(['filter', 'confirm']);

const name = ref('');
const minDbh = ref(null);
const maxDbh = ref(null);

const updateFilter = () => {
  emit('filter', {
    name: name.value,
    minDbh: minDbh.value,
    maxDbh: maxDbh.value
  });
};

const confirm = () => {
    emit('confirm');
};

const resetFilter = () => {
    name.value = '';
    minDbh.value = null;
    maxDbh.value = null;
    updateFilter();
};
</script>

<style scoped>
.filter-bar {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 8px 15px;
    background: var(--card-bg);
    border-radius: 4px;
    box-shadow: 0 2px 6px var(--shadow-color);
    pointer-events: auto;
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
}

input {
    padding: 4px 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 13px;
    width: 120px;
    background: var(--bg-color);
    color: var(--text-color);
}

.input-short {
    width: 60px;
}

.btn-reset {
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    color: var(--text-color);
}

.btn-reset:hover {
    background: var(--border-color);
}

.btn-confirm {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    margin-right: 5px;
}

.btn-confirm:hover {
    opacity: 0.9;
}
</style>
