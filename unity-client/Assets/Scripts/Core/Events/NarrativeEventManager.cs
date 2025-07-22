using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Collections;

public class NarrativeEventManager : MonoBehaviour
{
    [SerializeField] private Image _opacityImage;
    [SerializeField] private Canvas _canvas;

    [SerializeField] private RectTransform _leftCharactersAnchor;
    [SerializeField] private RectTransform _rightCharactersAnchor;
    [SerializeField] private GameObject _talkingCharacterPrefab;
    public static NarrativeEventManager Instance { get; private set; }


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
    }

    private void Start()
    {
        if (_canvas != null && Camera.main != null)
        {
            _canvas.worldCamera = Camera.main;
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void SetUpNarrativeEvent(string eventId, List<string> characterIds)
    {
        _opacityImage.gameObject.SetActive(true);
        StartCoroutine(FadeInOpacityBackground());
    }

    private IEnumerator FadeInOpacityBackground(float duration = 1f)
    {
        float time = 0f;
        float startAlpha = 0f;
        float targetAlpha = 0.8f;

        while (time < duration)
        {
            time += Time.deltaTime;
            float alpha = Mathf.Lerp(startAlpha, targetAlpha, time / duration);
            _opacityImage.color = new Color(_opacityImage.color.r, _opacityImage.color.g, _opacityImage.color.b, alpha);
            yield return null;
        }
    }
}
