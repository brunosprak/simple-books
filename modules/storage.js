export function createStorage(namespace, storage = window.localStorage) {
  const key = (name) => `${namespace}:${name}`;
  return {
    key,
    get(name, fallback = null) {
      try {
        const value = storage.getItem(key(name));
        return value === null ? fallback : value;
      } catch (_error) {
        return fallback;
      }
    },
    getJson(name, fallback) {
      try {
        const value = storage.getItem(key(name));
        return value === null ? fallback : JSON.parse(value);
      } catch (_error) {
        return fallback;
      }
    },
    set(name, value) {
      try {
        storage.setItem(key(name), value);
        return true;
      } catch (_error) {
        return false;
      }
    },
    setJson(name, value) {
      return this.set(name, JSON.stringify(value));
    },
    remove(name) {
      try {
        storage.removeItem(key(name));
        return true;
      } catch (_error) {
        return false;
      }
    }
  };
}
