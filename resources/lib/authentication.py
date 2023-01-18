import xbmcgui
import xbmc
from resources.lib.mediaset import Mediaset
from collections import namedtuple
from phate89lib import kodiutils, staticutils # pyright: reportMissingImports=false

ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92

# Define a class for the Dialog to show the URL
class Authentication(xbmcgui.WindowDialog):
  # Opening a xbmcgui.Window does not work, since the open settings dialog prevents this (http://forum.kodi.tv/showthread.php?tid=262100&pid=2263074#pid2263074)
  # Use xbmcgui.WindowDiaolog to be able to show the QR-code image
  
  def __init__(self, interval=3, maxRetry=100):

    self.med = Mediaset()
    self.log = kodiutils.log
    self.interval = interval
    self.maxRetry = maxRetry
    self.retry = 0

  def onControl(self, control):
    kodiutils.notify('onControl %s' % (control.getId()), icon=kodiutils.getMedia('notify.png'))
    pass

  def onFocus(self, control):
    kodiutils.notify('onControl %s' % (control.getId()), icon=kodiutils.getMedia('notify.png'))
    pass

  def onClick(self, control):
    kodiutils.notify('onClick %s' % (control), icon=kodiutils.getMedia('notify.png'))
    pass

  def onAction(self, action):
    # the window will be closed with any key
    # kodiutils.notify('%s - %s' % (action.getId(), action.getButtonCode()), icon=kodiutils.getMedia('notify.png'))
    if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
      self.log('Authentication Dialog Exit')
      self.retry = self.maxRetry
      self.close()

  def open(self):
    account = self.med.getAccount()
    screen_x = self.getWidth()
    screen_y = self.getHeight()
    win_width = int(screen_x * 3 / 5)
    win_height = int(screen_y * 3 / 5)
    win_x = int((screen_x - win_width) / 2)
    win_y = int((screen_y - win_height) / 2)
    win_x_offset = 25
    win_y_offset = 25
    win_line_height = 50

    Rectangle = namedtuple('Rectangle', 'x y width height')

    self.img_fade = xbmcgui.ControlImage(0, 0, screen_x, screen_y, kodiutils.getMedia('estuary-backdrop.png'), colorDiffuse='0xAA000000')
    self.img_bg = xbmcgui.ControlImage(win_x, win_y, win_width, win_height, kodiutils.getMedia('estuary-background.jpg'))

    img_qrcode_dim = Rectangle(x=(win_x + int((win_width-win_height/2)/2)), y=(win_y+win_y_offset), width=int(win_height/2), height=int(win_height/2))
    self.img_qrcode = xbmcgui.ControlImage(**img_qrcode_dim._asdict(), filename=kodiutils.getMedia('qr_code.png'))

    lbl_instruction_dim = Rectangle(x=(win_x + win_x_offset), y=int(img_qrcode_dim.y + img_qrcode_dim.height + win_line_height/2), width=int(win_width-win_x_offset*2), height=win_line_height)
    self.lbl_instruction = xbmcgui.ControlLabel(**lbl_instruction_dim._asdict(), label="[I]{}[/I]".format(account['action_url']), alignment=6, font='font14', textColor='0xFFFFFFFF')
    lbl_code_dim = Rectangle(x=(win_x + win_x_offset), y=int(lbl_instruction_dim.y + lbl_instruction_dim.height), width=int(win_width-win_x_offset*2), height=win_line_height)
    self.lbl_code = xbmcgui.ControlLabel(**lbl_code_dim._asdict(), label="[B]{}[/B]".format(account['action_pin']), alignment=6, font='font14', textColor='0xFF9D4DE1')
    
    self.addControls([self.img_fade, self.img_bg, self.img_qrcode, self.lbl_instruction, self.lbl_code])

    self.show()

  def auth(self):
    if self.med.isPaired():
      return True
    if self.med.registerDevice():
      self.open()
      self.monitor = xbmc.Monitor()
      self.retry = 0
      while self.retry < self.maxRetry and not(self.monitor.abortRequested()):
        self.retry = self.retry + 1
        if self.monitor.waitForAbort(self.interval):
          break
        if self.med.pair():
          break
      self.close()
    return self.med.isPaired()