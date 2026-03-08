import { ref, computed } from 'vue';
import { locales } from '../config/locales';

const currentLocale = ref('zh');

export function useI18n() {
    const locale = computed({
        get: () => currentLocale.value,
        set: (val) => {
            if (locales[val]) {
                currentLocale.value = val;
            }
        }
    });

    const t = (path) => {
        const keys = path.split('.');
        let current = locales[currentLocale.value];

        for (const key of keys) {
            if (current && current[key] !== undefined) {
                current = current[key];
            } else {
                console.warn(`Missing translation for key: ${path} in locale: ${currentLocale.value}`);
                return path;
            }
        }
        return current;
    };

    return {
        locale,
        t
    };
}
