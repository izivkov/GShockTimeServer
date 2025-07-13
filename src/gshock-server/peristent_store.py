import json
import os

class PersistentMap:
    def __init__(self, filepath):
        """
        Initialize the map and optionally load existing data from disk.
        """
        self.filepath = filepath
        self.data = {}
        self._load()

    def _load(self):
        """
        Load the data from disk if the file exists.
        """
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load map from {self.filepath}: {e}")
                self.data = {}
        else:
            self.data = {}

    def _save(self):
        """
        Save the current data to disk.
        """
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save map to {self.filepath}: {e}")

    def add(self, key, value):
        """
        Add or update a key-value pair.
        """
        self.data[key] = value
        self._save()

    def delete(self, key):
        """
        Delete a key-value pair.
        """
        if key in self.data:
            del self.data[key]
            self._save()

    def clear(self):
        """
        Clear all key-value pairs.
        """
        self.data.clear()
        self._save()

    def get(self, key, default=None):
        """
        Get the value for a key, or return default.
        """
        return self.data.get(key, default)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)
