using UnityEngine;
using UnityEngine.SceneManagement;

public class BackToMenu : MonoBehaviour
{
    public void ReturnToLogin()
    {
        SceneManager.LoadScene("LoginScene");
    }
}