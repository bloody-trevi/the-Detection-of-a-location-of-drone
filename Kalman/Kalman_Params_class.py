class KalmanParam:
    """
    칼만 필터에 필요한 행렬과 벡터들을 저장해주는 클래스

    """

    def __init__(self, A, H, Q, R, x, P):
        """
        각 행렬을 초기화 해주는 생성자

        :param A: 시스템 행렬, (nxn) 행렬
        :param H: 출력 행렬, (mxn) 행렬
        :param Q: 칼만 필터에서 w_k 벡터의 공분산 행렬, (nxn) 대각 행렬
        :param R: 칼만 필터에서 v_k 벡터의 공분산 행렬, (mxm) 대각 행렬
        :param x: 상태 변수, (nx1) 열벡터
        :param P: 오차 공분산(x가 가지는 정규 분포에서이 공분산)
        """
        self.A = A
        self.H = H
        self.Q = Q
        self.R = R
        self.x = x
        self.P = P

    def set_mats(self, A, H, Q, R):
        """
        각 행렬 설정
        
        :param A: 시스템 행렬, (nxn) 행렬
        :param H: 출력 행렬, (mxn) 행렬
        :param Q: 칼만 필터에서 w_k 벡터의 공분산 행렬, (nxn) 대각 행렬
        :param R: 칼만 필터에서 v_k 벡터의 공분산 행렬, (mxm) 대각 행렬
        :return: 없음
        """
        self.A = A
        self.H = H
        self.Q = Q
        self.R = R

    def set_x_P(self, x, P):
        """
        상태 변수와 오차 공분산 설정
        
        :param x: 상태 변수
        :param P: 오차 공분산
        :return: 없음
        """
        self.x = x
        self.P = P

    def get_mats(self):
        """
        각 행렬 반환
        
        :return: 시스템 행렬 A, 출력 행렬 H, Q, R 
        """
        return self.A, self.H, self.Q, self.R

    def get_x(self):
        """
        상태 변수 반환
        
        :return: 상태 변수 x
        """
        return self.x

    def get_P(self):
        """
        오차 공분산 반환
        
        :return: 오차 공분산 P
        """
        return self.P
