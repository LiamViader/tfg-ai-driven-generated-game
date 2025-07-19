using UnityEngine;
using DG.Tweening;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;
public class CharacterContextualUI : MonoBehaviour
{
    [SerializeField] private Canvas _canvas;
    [SerializeField] private Transform _itemsParent;
    [SerializeField] private GameObject _menuItemPrefab;


    private bool _showing = false;
    public bool IsAnimatingShow { get; private set; } = false;
    public bool IsAnimatingHide { get; private set; } = false;

    private System.Action _onHideCallback;

    private Dictionary<string, ContextualMenuItem> _currentMenuItems = new();

    private string _characterId;

    private void OnEnable()
    {
        if (_canvas != null && Camera.main != null)
        {
            _canvas.worldCamera = Camera.main;
        }

        if (UIManager.Instance != null)
        {
            UIManager.Instance.OnCharacterOptionsUpdated += OnCharacterOptionsDataUpdated;
        }
    }

    private void OnDisable()
    {
        if (UIManager.Instance != null)
        {
            UIManager.Instance.OnCharacterOptionsUpdated -= OnCharacterOptionsDataUpdated;
        }
    }

    public void Initialize(string characterId)
    {
        _characterId = characterId;
        RefreshMenuItems();
    }

    void Update()
    {
        if (_showing && !IsAnimatingShow && !IsAnimatingHide && Input.GetMouseButtonDown(0))
        {
            if (!IsPointerOverAnyItemWithSpacing())
            {
                HideContextualMenu();
            }
        }
    }

    private bool IsPointerOverAnyItemWithSpacing()
    {
        Vector2 mouseWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);

        float spacing = 0f;
        VerticalLayoutGroup layoutGroup = _itemsParent.GetComponent<VerticalLayoutGroup>();
        if (layoutGroup != null)
        {
            spacing = layoutGroup.spacing;
        }

        foreach (Transform item in _itemsParent)
        {
            RectTransform rect = item.GetComponent<RectTransform>();
            if (rect == null) continue;

            Vector3[] worldCorners = new Vector3[4];
            rect.GetWorldCorners(worldCorners);

            float extra = spacing / 2f;

            if (PointInExpandedRect(mouseWorldPos, worldCorners, extra))
            {
                return true;
            }
        }

        return false;
    }

    private bool PointInExpandedRect(Vector2 point, Vector3[] corners, float verticalPadding)
    {
        float minX = corners[0].x;
        float maxX = corners[2].x;
        float minY = corners[0].y - verticalPadding;
        float maxY = corners[2].y + verticalPadding;

        return point.x >= minX && point.x <= maxX &&
               point.y >= minY && point.y <= maxY;
    }

    public void ShowContextualMenu(Transform contextualMenuOrigin, bool right, System.Action onHide = null)
    {
        if (_canvas == null || IsAnimatingShow || IsAnimatingHide) return;

        RefreshMenuItems();

        if (_currentMenuItems.Count == 0)
        {
            Debug.Log($"No hay opciones de interacción disponibles para el personaje {_characterId}.");
            return;
        }

        _onHideCallback = onHide;

        RectTransform rect = _canvas.GetComponent<RectTransform>();
        rect.pivot = right ? new Vector2(0f, 1f) : new Vector2(1f, 1f);

        _canvas.gameObject.SetActive(true);
        _canvas.transform.SetParent(contextualMenuOrigin, worldPositionStays: false);
        _canvas.transform.localPosition = Vector3.zero;
        _canvas.transform.localRotation = Quaternion.identity;
        _canvas.transform.localScale = Vector3.one;

        _showing = true;
        AnimateAppearItems();
    }

    public void HideContextualMenu()
    {
        if (_canvas == null || !gameObject.activeInHierarchy || IsAnimatingHide || IsAnimatingShow) return;

        AnimateHideItems(() =>
        {
            _canvas.gameObject.SetActive(false);

        });
    }

    public void AnimateAppearItems()
    {
        int childCount = _itemsParent.childCount;
        float itemDuration = 0.4f;
        float overlap = 0.2f;

        IsAnimatingShow = true;

        Sequence fullSequence = DOTween.Sequence();

        for (int i = 0; i < childCount; i++)
        {
            Transform item = _itemsParent.GetChild(i);
            RectTransform rt = item.GetComponent<RectTransform>();
            CanvasGroup cg = item.GetComponent<CanvasGroup>();

            if (cg == null)
                cg = item.gameObject.AddComponent<CanvasGroup>();

            rt.localScale = new Vector3(1f, 0f, 1f);
            cg.alpha = 0f;

            Sequence itemSequence = DOTween.Sequence();
            itemSequence.Join(rt.DOScaleY(1f, itemDuration).SetEase(Ease.OutBack));
            itemSequence.Join(cg.DOFade(1f, itemDuration * 0.8f).SetEase(Ease.Linear));

            fullSequence.Insert(i * (itemDuration - overlap), itemSequence);
        }

        float totalDuration = itemDuration + (childCount - 1) * (itemDuration - overlap);
        fullSequence.OnComplete(() => IsAnimatingShow = false);
    }

    public void AnimateHideItems(System.Action onComplete)
    {
        int childCount = _itemsParent.childCount;
        float duration = 0.2f;

        IsAnimatingHide = true;

        Sequence hideSequence = DOTween.Sequence();

        for (int i = 0; i < childCount; i++)
        {
            Transform item = _itemsParent.GetChild(i);
            RectTransform rt = item.GetComponent<RectTransform>();
            CanvasGroup cg = item.GetComponent<CanvasGroup>();

            if (cg == null)
                cg = item.gameObject.AddComponent<CanvasGroup>();

            hideSequence.Join(rt.DOScaleX(0f, duration).SetEase(Ease.InBack));
            hideSequence.Join(cg.DOFade(0f, duration * 1.5f).SetEase(Ease.Linear));
        }

        _showing = false;
        _onHideCallback?.Invoke();
        _onHideCallback = null;
        hideSequence.OnComplete(() =>
        {
            IsAnimatingHide = false;
            onComplete?.Invoke();
        });
    }

    public void AddOption(string conditionId, string label, System.Action onClickCallback)
    {
        if (_menuItemPrefab == null)
        {
            Debug.LogError("ContextualMenuItem prefab is not assigned to CharacterContextualUI!");
            return;
        }

        // Si ya existe una opción con este conditionId, la actualizamos
        if (_currentMenuItems.TryGetValue(conditionId, out var existingItem))
        {
            existingItem.Initialize(label, onClickCallback, conditionId);
        }
        else
        {
            GameObject menuItemGO = Instantiate(_menuItemPrefab, _itemsParent);
            ContextualMenuItem menuItem = menuItemGO.GetComponent<ContextualMenuItem>();
            if (menuItem == null)
            {
                Debug.LogError("ContextualMenuItem prefab is missing ContextualMenuItem component!");
                Destroy(menuItemGO);
                return;
            }
            menuItem.Initialize(label, onClickCallback, conditionId);
            _currentMenuItems[conditionId] = menuItem;
            Debug.Log($"Added new menu item for condition ID: {conditionId}");
        }
    }

    public void RemoveOption(string conditionId)
    {
        if (_currentMenuItems.TryGetValue(conditionId, out var menuItem))
        {
            Destroy(menuItem.gameObject);
            _currentMenuItems.Remove(conditionId);
            Debug.Log($"Removed menu item for condition ID: {conditionId}");
        }
    }

    public void ClearAllOptions()
    {
        foreach (var item in _currentMenuItems.Values)
        {
            if (item != null) Destroy(item.gameObject);
        }
        _currentMenuItems.Clear();
        Debug.Log("Cleared all contextual menu options.");
    }

    public void RefreshMenuItems()
    {
        // 1. Obtener la lista actual de opciones para este personaje del GameManager
        // Estas opciones incluyen solo aquellas que provienen de GameEvents, pero el menú es genérico.
        List<CharacterOptionEventData> currentEventOptions = GameManager.Instance.GetCharacterContextualOptions(_characterId);

        // 2. Aquí puedes añadir otras opciones que no sean de eventos si las necesitas
        // Por ejemplo:
        // List<GenericCharacterOptionData> otherOptions = GetOtherCharacterOptions(_characterId); 
        // var allOptions = new List<SomeCommonInterfaceForOptionData>();
        // allOptions.AddRange(currentEventOptions);
        // allOptions.AddRange(otherOptions);

        // Para este ejemplo, solo trabajamos con currentEventOptions para simplificar
        var allOptions = currentEventOptions; // En un escenario real, sería allOptions si tuvieras más fuentes

        // 3. Identificar opciones a eliminar (están en la UI pero ya no en los datos)
        var optionsToRemove = _currentMenuItems.Keys
            .Where(condId => !allOptions.Any(opt => opt.conditionId == condId))
            .ToList();

        foreach (var condId in optionsToRemove)
        {
            RemoveOption(condId);
        }

        // 4. Crear/Actualizar y Ordenar las opciones
        // Para asegurar el orden, primero las añadimos/actualizamos y luego las reorganizamos.
        // O más eficientemente, destruimos todas y las recreamos en orden.
        // Dado que ya tienes un sistema de deltas, vamos a reconstruir el orden manteniendo los GameObjects existentes.

        // Limpiar _itemsParent para reconstruir el orden
        foreach (Transform child in _itemsParent)
        {
            // Solo desactivar, no destruir, si el item aún existe en _currentMenuItems
            if (_currentMenuItems.ContainsKey(child.GetComponent<ContextualMenuItem>().ConditionId)) // Asumiendo que ContextualMenuItem tiene ConditionId
            {
                child.gameObject.SetActive(false); // Desactiva para reordenar
                child.SetParent(null); // Desvincula temporalmente
            }
            else // Si no está en _currentMenuItems, es un item a destruir (ya debería estar fuera por optionsToRemove)
            {
                Destroy(child.gameObject);
            }
        }
        // Limpiar el _itemsParent completamente antes de añadir en orden
        _itemsParent.DetachChildren(); // Desvincula todos los hijos restantes


        // Ordenar las opciones por ConditionId para asegurar el mismo orden siempre
        var orderedOptions = allOptions.OrderBy(opt => opt.conditionId).ToList();

        foreach (var optionData in orderedOptions)
        {
            // Define el callback según el tipo de opción
            System.Action onClickAction;

            // Ejemplo: si solo GameEvents
            onClickAction = () => GameManager.Instance.TriggerEvent(optionData.eventId);

            // Si tuvieras diferentes tipos de opciones (más allá de CharacterOptionEventData),
            // usarías un 'switch' o una lógica más compleja aquí.
            // Por ejemplo:
            // if (optionData is CharacterOptionEventData eventData)
            // {
            //    onClickAction = () => GameManager.Instance.TriggerEvent(eventData.EventId);
            // }
            // else if (optionData is CharacterInfoOptionData infoData)
            // {
            //    onClickAction = () => UIManager.Instance.ShowCharacterInfoPanel(infoData.CharacterId);
            // }

            // Añadir/Actualizar la opción y re-parentarla al _itemsParent en el orden deseado
            AddOption(optionData.conditionId, optionData.menuLabel, onClickAction);
            // Asegurarse de que el GameObject del ContextualMenuItem recién creado/actualizado
            // se reparente correctamente al _itemsParent y esté activo
            if (_currentMenuItems.TryGetValue(optionData.conditionId, out var menuItem))
            {
                menuItem.transform.SetParent(_itemsParent);
                menuItem.gameObject.SetActive(true);
            }
        }

        // Reconstruir el Layout Group
        LayoutRebuilder.ForceRebuildLayoutImmediate(_itemsParent.GetComponent<RectTransform>());
        Canvas.ForceUpdateCanvases(); // Asegura que el layout se actualice antes de animar
    }

    // Nuevo: Handler para el evento de actualización de opciones de personaje
    private void OnCharacterOptionsDataUpdated(string updatedCharacterId)
    {
        // Solo refrescar si este menú pertenece al personaje actualizado
        if (updatedCharacterId == _characterId)
        {
            RefreshMenuItems();
        }
    }
}
