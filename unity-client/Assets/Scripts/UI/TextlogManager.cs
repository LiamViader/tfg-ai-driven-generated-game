using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using System.Collections;
using DG.Tweening;

public class TextlogManager : MonoBehaviour
{
    [SerializeField] private TMP_Text _characterNameTextLeft;
    [SerializeField] private TMP_Text _characterNameTextRight;
    [SerializeField] private GameObject _characterNameLeft;
    [SerializeField] private GameObject _characterNameRight;
    [SerializeField] private TMP_Text _textlogText;

    [SerializeField] private float _charRevealSpeed = 0.02f;

    private string _fullText = "";
    private int _visibleCharCount = 0;
    private Coroutine _typingCoroutine;


    public void AppendText(string newText)
    {
        if (string.IsNullOrEmpty(newText)) return;

        _fullText += newText;

        if (_typingCoroutine == null)
        {
            Debug.Log("LAUNCHING COROUTINE");
            _typingCoroutine = StartCoroutine(TypeTextCoroutine());
        }
    }

    public void Clear()
    {
        _fullText = "";
        _visibleCharCount = 0;
        _textlogText.text = "";
    }

    public bool HasShownAll()
    {
        return _visibleCharCount >= _fullText.Length;
    }

    private IEnumerator TypeTextCoroutine()
    {
        while (true)
        {
            // Mostrar un nuevo carácter si hay más por mostrar
            if (_visibleCharCount < _fullText.Length)
            {
                _visibleCharCount++;
                _textlogText.text = _fullText.Substring(0, _visibleCharCount);
                yield return new WaitForSeconds(_charRevealSpeed);
            }
            else
            {
                // Esperar un frame y volver a chequear si llegó nuevo texto
                yield return null;
            }
        }
    }

    public void UpdateLeftName(string text, bool show)
    {
        _characterNameTextLeft.text = text;
        _characterNameLeft.SetActive(show);
    }

    public void UpdateRightName(string text, bool show)
    {
        _characterNameTextRight.text = text;
        _characterNameRight.SetActive(show);
    }

    public void UpdateText(string text)
    {
        _textlogText.text = text;
    }

}
