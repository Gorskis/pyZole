import pygame
from pygame import VIDEORESIZE
from app_state import AppState
from bordered_screen import BorderedScreen
from resource_manager import resources
from screen_manager import ScreenManager
from settings import AppSettings

if __name__ == '__main__':
    pygame.init() 
    screen_data = BorderedScreen((1000, 562))
    pygame.display.set_caption("pyZole")
    pygame.display.set_icon(resources.window_icon)
    clock = pygame.time.Clock() 
    done = False
    app_state = AppState()
    app_state.settings = AppSettings()
    # TODO load settings
    screen_manager = ScreenManager(app_state)
    app_state = screen_manager.app_state

    while not app_state.exit_app:
        current_screen = screen_manager.get_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_state.exit_app = True
            elif event.type == VIDEORESIZE:
                screen_data.resize_screen(event.size)
            else:
                m_pos = pygame.mouse.get_pos()
                m_sub_pos = screen_data.get_mouse_sub_pos(m_pos)
                # scaled/translated mouse position onto sub-screen
                # Pass events to active GUI
                current_screen.handle_event(event, m_sub_pos)
        current_screen.update()
        # background
        screen_data.draw_background()
        # Pass drawing to GUI
        current_screen.draw_to(screen_data.sub_screen)
        # Scale and place sub-screen on app-screen
        screen_data.apply_sub_screen()
        pygame.display.flip()
        clock.tick(12)
    pygame.quit()
