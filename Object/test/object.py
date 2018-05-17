import wait_for_seconds
class test:
    @staticmethod
    def wait_for_seconds(*args, **kwargs):
        return wait_for_seconds.wait_for_seconds(*args, **kwargs)


if __name__ == '__main__':
    
    test.wait_for_seconds('kati', seconds = 8)
