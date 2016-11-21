import pytest

from helix import Helix


@pytest.fixture(scope="session")
def helix():
    return Helix(
        staging=True,
        grant_type="client_credentials",
        client_id="CL-7ICCDTTMGWK7VHTJIHCPWZZ7EEZBID7Z",
        client_secret="CS-B7XBHYQLWURKBV3ZXVBGK7SXIZ7JGKTG",
        genomic_client_id="CL-AQ3EJLBNNDE7LJZYVGUOMM4WA5HBOHEL",
        genomic_client_secret="CS-Y5MFWTTZU67LOIEBOWFT2LE7DEI3OPP7"
    )
