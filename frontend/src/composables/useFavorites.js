import { ref } from 'vue'
import { toggleFavorite, getFavoriteList, checkFavorite } from '../api/favorite'

const favMap = ref({})
const loaded = ref(false)
let loadingPromise = null

export function useFavorites() {
  function isFav(spuId) {
    return !!favMap.value[String(spuId)]
  }

  async function toggle(spuId) {
    const id = String(spuId)
    const res = await toggleFavorite(spuId)
    const next = { ...favMap.value }
    if (res.data.is_favorited) {
      next[id] = true
    } else {
      delete next[id]
    }
    favMap.value = next
    return res.data.is_favorited
  }

  async function loadAll(force = false) {
    if (loaded.value && !force) {
      return buildListFromMap()
    }
    if (loadingPromise && !force) return loadingPromise
    loadingPromise = _doLoad()
    return loadingPromise
  }

  async function _doLoad() {
    try {
      const res = await getFavoriteList()
      const list = res.data || res.items || []
      const map = {}
      list.forEach((item) => { map[String(item.spu_id)] = true })
      favMap.value = map
      loaded.value = true
      return list
    } finally {
      loadingPromise = null
    }
  }

  function buildListFromMap() {
    return Object.keys(favMap.value).map((id) => ({ spu_id: Number(id) }))
  }

  async function check(spuId) {
    const id = String(spuId)
    const res = await checkFavorite(spuId)
    const next = { ...favMap.value }
    if (res.data.is_favorited) {
      next[id] = true
    } else {
      delete next[id]
    }
    favMap.value = next
    return res.data.is_favorited
  }

  async function ensureLoaded() {
    if (!loaded.value) await loadAll()
  }

  return { isFav, toggle, loadAll, check, ensureLoaded, loaded }
}
