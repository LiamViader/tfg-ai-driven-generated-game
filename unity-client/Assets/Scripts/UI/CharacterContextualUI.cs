using UnityEngine;
using DG.Tweening;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Linq;
public class CharacterContextualUI : MonoBehaviour
{
    [SerializeField] private Canvas _canvas;
    [SerializeField] private Transform _itemsParent;
    [SerializeField] private GameObject _menuItemPrefab;
    [SerializeField] private Transform _contextualMenuOriginRight;
    [SerializeField] private Transform _contextualMenuOriginLeft;
    [SerializeField] private Transform _characterNameOrigin;
    [SerializeField] private Canvas _nameCanvas;
    [SerializeField] private TMP_Text _characterNameText;
    [SerializeField] private TMP_Text _characterAliasText;

    private Tween _nameFadeTween;

    private bool _showing = false;
    public bool IsAnimatingShow { get; private set; } = false;
    public bool IsAnimatingHide { get; private set; } = false;

    private CanvasGroup _nameCanvasGroup;

    private System.Action _onHideCallback;

    private Dictionary<string, ContextualMenuItem> _currentMenuItems = new();

    private string _characterId;

    private bool _triggeringCondition = false;


    private void OnEnable()
    {
        if (_canvas != null && Camera.main != null && _nameCanvas != null)
        {
            _canvas.worldCamera = Camera.main;
            _nameCanvas.worldCamera = Camera.main;
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
    private void Awake()
    {
        _nameCanvasGroup = _nameCanvas.GetComponent<CanvasGroup>();
        if (_nameCanvasGroup == null)
        {
            _nameCanvasGroup = _nameCanvas.gameObject.AddComponent<CanvasGroup>();
        }
    }
    public void Initialize(string characterId, SpriteRenderer characterSpriteRenderer, string name, string alias)
    {
        _characterId = characterId;
        UpdateContextualMenuOrigins(characterSpriteRenderer);
        RefreshMenuItems();
        _characterAliasText.text = alias;
        _characterNameText.text = name;
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

    private void UpdateContextualMenuOrigins(SpriteRenderer characterSpriteRenderer)
    {
        Bounds bounds = characterSpriteRenderer.bounds;

        Vector3 topLeft = new Vector3(bounds.min.x - 0.2f, bounds.max.y - 0.5f, transform.position.z);
        Vector3 topRight = new Vector3(bounds.max.x + 0.2f, bounds.max.y - 0.5f, transform.position.z);
        Vector3 topCenter = new Vector3(bounds.center.x, bounds.max.y, transform.position.z);

        if (_contextualMenuOriginLeft != null)
            _contextualMenuOriginLeft.position = topLeft;

        if (_contextualMenuOriginRight != null)
            _contextualMenuOriginRight.position = topRight;

        if (_characterNameOrigin != null)
            _characterNameOrigin.position = topCenter;
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

    public void ShowContextualMenu(bool right, System.Action onHide = null)
    {
        if (_canvas == null || IsAnimatingShow || IsAnimatingHide) return;

        RefreshMenuItems();

        _onHideCallback = onHide;

        RectTransform rect = _canvas.GetComponent<RectTransform>();
        rect.pivot = right ? new Vector2(0f, 1f) : new Vector2(1f, 1f);
        Transform contextualMenuOrigin = right ? _contextualMenuOriginRight : _contextualMenuOriginLeft;
        _canvas.gameObject.SetActive(true);
        _canvas.transform.SetParent(contextualMenuOrigin, worldPositionStays: false);
        _canvas.transform.localPosition = Vector3.zero;
        _canvas.transform.localRotation = Quaternion.identity;
        _canvas.transform.localScale = Vector3.one;

        _nameCanvas.gameObject.SetActive(true);
        AnimateShowNameCanvas();

        _showing = true;
        AnimateAppearItems();
    }

    public void HideContextualMenu()
    {
        if (_canvas == null || !gameObject.activeInHierarchy || IsAnimatingHide || IsAnimatingShow || _triggeringCondition) return;

        AnimateHideItems(() =>
        {
            _canvas.gameObject.SetActive(false);
            
        });
        AnimateHideNameCanvas();
    }

    private void AnimateShowNameCanvas()
    {
        _nameFadeTween?.Kill();

        _nameCanvasGroup.alpha = 0f;
        _nameCanvasGroup.DOFade(1f, 0.25f).SetEase(Ease.OutQuad);
    }

    private void AnimateHideNameCanvas()
    {
        _nameFadeTween?.Kill();

        _nameFadeTween = _nameCanvasGroup.DOFade(0f, 0.2f)
            .SetEase(Ease.InQuad)
            .OnComplete(() =>
            {
                _nameCanvas.gameObject.SetActive(false);
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

        // Si ya existe una opci�n con este conditionId, la actualizamos
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
        // Estas opciones incluyen solo aquellas que provienen de GameEvents, pero el men� es gen�rico.
        List<CharacterOptionEventData> currentEventOptions = GameManager.Instance.GetCharacterContextualOptions(_characterId);

        // 2. Aqu� puedes a�adir otras opciones que no sean de eventos si las necesitas
        // Por ejemplo:
        // List<GenericCharacterOptionData> otherOptions = GetOtherCharacterOptions(_characterId); 
        // var allOptions = new List<SomeCommonInterfaceForOptionData>();
        // allOptions.AddRange(currentEventOptions);
        // allOptions.AddRange(otherOptions);

        // Para este ejemplo, solo trabajamos con currentEventOptions para simplificar
        var allOptions = currentEventOptions; // En un escenario real, ser�a allOptions si tuvieras m�s fuentes

        // 3. Identificar opciones a eliminar (est�n en la UI pero ya no en los datos)
        var optionsToRemove = _currentMenuItems.Keys
            .Where(condId => !allOptions.Any(opt => opt.conditionId == condId))
            .ToList();

        foreach (var condId in optionsToRemove)
        {
            RemoveOption(condId);
        }

        // 4. Crear/Actualizar y Ordenar las opciones
        // Para asegurar el orden, primero las a�adimos/actualizamos y luego las reorganizamos.
        // O m�s eficientemente, destruimos todas y las recreamos en orden.
        // Dado que ya tienes un sistema de deltas, vamos a reconstruir el orden manteniendo los GameObjects existentes.

        // Limpiar _itemsParent para reconstruir el orden
        foreach (Transform child in _itemsParent)
        {
            // Solo desactivar, no destruir, si el item a�n existe en _currentMenuItems
            ContextualMenuItem menu_item = child.GetComponent<ContextualMenuItem>();
            string conditionId = menu_item?.ConditionId;
            if (conditionId != null)
            {
                if (_currentMenuItems.ContainsKey(conditionId)) // Asumiendo que ContextualMenuItem tiene ConditionId
                {
                    child.gameObject.SetActive(false); // Desactiva para reordenar
                    child.SetParent(null); // Desvincula temporalmente
                }
                else // Si no est� en _currentMenuItems, es un item a destruir (ya deber�a estar fuera por optionsToRemove)
                {
                    Destroy(child.gameObject);
                }
            }

        }
        // Limpiar el _itemsParent completamente antes de a�adir en orden
        _itemsParent.DetachChildren(); // Desvincula todos los hijos restantes


        // Ordenar las opciones por ConditionId para asegurar el mismo orden siempre
        var orderedOptions = allOptions.OrderBy(opt => opt.conditionId).ToList();

        foreach (var optionData in orderedOptions)
        {
            // Define el callback seg�n el tipo de opci�n
            System.Action onClickAction;

            // Ejemplo: si solo GameEvents
            onClickAction = () => TriggerCondition(optionData.conditionId);

            // Si tuvieras diferentes tipos de opciones (m�s all� de CharacterOptionEventData),
            // usar�as un 'switch' o una l�gica m�s compleja aqu�.
            // Por ejemplo:
            // if (optionData is CharacterOptionEventData eventData)
            // {
            //    onClickAction = () => GameManager.Instance.TriggerEvent(eventData.EventId);
            // }
            // else if (optionData is CharacterInfoOptionData infoData)
            // {
            //    onClickAction = () => UIManager.Instance.ShowCharacterInfoPanel(infoData.CharacterId);
            // }

            // A�adir/Actualizar la opci�n y re-parentarla al _itemsParent en el orden deseado
            AddOption(optionData.conditionId, optionData.menuLabel, onClickAction);
            // Asegurarse de que el GameObject del ContextualMenuItem reci�n creado/actualizado
            // se reparente correctamente al _itemsParent y est� activo
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

    // Nuevo: Handler para el evento de actualizaci�n de opciones de personaje
    private void OnCharacterOptionsDataUpdated(string updatedCharacterId)
    {
        // Solo refrescar si este men� pertenece al personaje actualizado
        if (updatedCharacterId == _characterId)
        {
            RefreshMenuItems();
        }
    }

    private void TriggerCondition(string conditionId)
    {
        if (_triggeringCondition) return;

        _triggeringCondition = true;

        ActionHandler.Instance.RequestTriggerCondition(
            conditionId,
            () => {
                _triggeringCondition = false;
            },
            () => {
                _triggeringCondition = false;
            }
        );

    }
}
