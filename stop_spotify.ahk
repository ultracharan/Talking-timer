

; Stop the playback by sending the Play/Pause media key
Send("{Media_Play_Pause}")

; Wait for a brief moment to ensure the command is processed
Sleep(500)

; Minimize the Spotify window using its title
WinMinimize("Spotify")

; Exit the script
ExitApp()
