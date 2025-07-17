using UnityEngine;
using UnityEngine.UI;

public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }

    [SerializeField] private Button backgroundBlocker;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }

        if (backgroundBlocker != null)
            backgroundBlocker.gameObject.SetActive(false);
    }

    public void ShowBlocker(System.Action onClickOutside)
    {
        if (backgroundBlocker == null) return;

        backgroundBlocker.gameObject.SetActive(true);
        backgroundBlocker.onClick.RemoveAllListeners();
        backgroundBlocker.onClick.AddListener(() =>
        {
            onClickOutside?.Invoke();
            HideBlocker();
        });
    }

    public void HideBlocker()
    {
        if (backgroundBlocker == null) return;

        backgroundBlocker.onClick.RemoveAllListeners();
        backgroundBlocker.gameObject.SetActive(false);
    }
}
