import sqlite3

class dbHandler:

  DB_TABLE_LOG = 'log'
  DB_LOG_SERVER_NAME = 'server_name'
  DB_LOG_MESSAGE_ID = 'message_id'
  DB_LOG_OPERATION = 'operation_type'
  DB_LOG_MESSAGE_CONTENT = 'message_content'
  DB_LOG_AUTHOR_NAME = 'author_name'
  DB_LOG_CHANNEL_NAME = 'channel_name'
  DB_LOG_TIMESTAMP = 'timestamp'


  DB_TABLE_REACTION = 'reaction'
  DB_REACTION_SERVER_NAME = 'server_name'
  DB_REACTION_MESSAGE_ID = 'message_id'
  DB_REACTION_OPERATION = 'operation_type'
  DB_REACTION_MESSAGE = 'reaction_message'
  DB_REACTION_EMOJI = 'reaction_emoji'
  DB_REACTION_USER = 'reaction_user'
  DB_REACTION_CHANNEL_NAME = 'channel_name'

  OPERATION_REACT_ADD = 'A'
  OPERATION_REACT_DELETE = 'D'
  OPERATION_MESSAGE = 'A'
  OPERATION_EDIT = 'E'

  DB_CHANNEL_NAME = 'channel_name'

  def dbOpen(self):
    self.conn = sqlite3.connect(self.dbPath)

  def dbClose(self):
    self.conn.close()

  def createTableIfNotExist(self):
    if self.conn.cursor().execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0] == 0:
      c = self.conn.cursor()
      c.execute('CREATE table {0} ({1} TEXT, {2} TEXT, {3} TEXT, {4} TEXT, {5} TEXT, {6} TEXT, {7} TEXT)'.format(self.DB_TABLE_LOG, self.DB_LOG_SERVER_NAME, self.DB_LOG_CHANNEL_NAME, self.DB_LOG_MESSAGE_ID, self.DB_LOG_OPERATION, self.DB_LOG_MESSAGE_CONTENT, self.DB_LOG_AUTHOR_NAME, self.DB_LOG_TIMESTAMP))
      c.execute('CREATE table {0} ({1} TEXT, {2} TEXT, {3} TEXT, {4} TEXT, {5} TEXT, {6} TEXT, {7} TEXT)'.format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_CHANNEL_NAME, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER))

      self.conn.commit()
      return True
    else:
      return False

  def addLog(self, server_name, message_id, operation, message_content, author_name, channel_name, timestamp):
    c = self.conn.cursor()
    c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}) VALUES (?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_LOG, self.DB_LOG_SERVER_NAME, self.DB_LOG_MESSAGE_ID, self.DB_LOG_OPERATION, self.DB_LOG_MESSAGE_CONTENT, self.DB_LOG_AUTHOR_NAME, self.DB_LOG_CHANNEL_NAME, self.DB_LOG_TIMESTAMP), (str(server_name), str(message_id), str(operation), str(message_content), str(author_name), str(channel_name), str(timestamp)))
    self.conn.commit()
    return True

  def addReaction(self, server_name, message_id, operation, reaction_message, emoji, user, channel_name):
    c = self.conn.cursor()
    c.execute("INSERT INTO {0} ({1}, {2}, {3}, {4}, {5}, {6}, {7}) VALUES (?, ?, ?, ?, ?, ?, ?)".format(self.DB_TABLE_REACTION, self.DB_REACTION_SERVER_NAME, self.DB_REACTION_MESSAGE_ID, self.DB_REACTION_OPERATION, self.DB_REACTION_MESSAGE, self.DB_REACTION_EMOJI, self.DB_REACTION_USER, self.DB_REACTION_CHANNEL_NAME), (str(server_name), str(message_id), str(operation), str(reaction_message), str(emoji), str(user), str(channel_name)))
    self.conn.commit()
    return True

  def __init__(self, dbPath):
    self.dbPath = dbPath

    self.dbOpen()
    self.createTableIfNotExist()
