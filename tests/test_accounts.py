"""Tests for the account system: registering, logging in, searching, the leaderboard and the file."""
import pytest

from space_invaders.accounts import Client, ClientList


@pytest.fixture
def accounts_file(tmp_path):
    """Path to an accounts file inside a temporary folder (not created yet)."""
    return tmp_path / "Clientfile.txt"


def write_lines(path, *lines):
    path.write_text("".join(line + "\n" for line in lines))


def make_list(accounts_file, *names):
    """A client list containing the given usernames, each with password '<name>-pw'."""
    write_lines(accounts_file, *(f"{name},{name}-pw,Question?,answer,0,0" for name in names))
    return ClientList(str(accounts_file))


def usernames(clients):
    return [client.username for client in clients]


# --- Loading and saving --------------------------------------------------------

def test_missing_file_is_created_empty(accounts_file):
    clients = ClientList(str(accounts_file))
    assert accounts_file.exists()
    assert len(clients) == 0


def test_save_and_load_round_trip_keeps_every_field(accounts_file):
    clients = ClientList(str(accounts_file))
    clients.add_client(Client("zoe", "secret", "First pet?", "Rex", 40, 90))

    reloaded = ClientList(str(accounts_file))
    found, index = reloaded.find(Client("zoe"))
    assert found
    zoe = reloaded.clients[index]
    assert (zoe.question, zoe.answer) == ("First pet?", "Rex")
    assert (zoe.score, zoe.highest_score) == (40, 90)


def test_loading_sorts_clients_by_username(accounts_file):
    clients = make_list(accounts_file, "mike", "alice", "zoe", "bob")
    assert usernames(clients.clients) == ["alice", "bob", "mike", "zoe"]


def test_old_file_formats_still_load(accounts_file):
    write_lines(
        accounts_file,
        "carol, pw3, Town?, Leeds, 10, 300",  # old ", " separated style
        "dave,pw4,Colour?,red",               # no score columns
        "",                                   # blank line
        "broken,line",                        # too few fields
        "erin,pw5,Food?,pie,abc,",            # unreadable scores
    )
    clients = ClientList(str(accounts_file))
    assert usernames(clients.clients) == ["carol", "dave", "erin"]
    carol, dave, erin = clients.clients
    assert (carol.score, carol.highest_score) == (10, 300)
    assert (dave.score, dave.highest_score) == (0, 0)
    assert (erin.score, erin.highest_score) == (0, 0)


# --- Registering, logging in and deleting ----------------------------------------

def test_register_adds_client_in_sorted_position_and_saves(accounts_file):
    clients = make_list(accounts_file, "alice", "zoe")
    clients.add_client(Client("mike", "pw", "Q?", "A"))

    assert usernames(clients.clients) == ["alice", "mike", "zoe"]
    assert usernames(ClientList(str(accounts_file)).clients) == ["alice", "mike", "zoe"]


def test_login_finds_user_and_checks_password(accounts_file):
    clients = make_list(accounts_file, "alice", "bob")
    found, index = clients.find(Client("bob"))
    assert found
    assert clients.clients[index].password == "bob-pw"
    assert clients.clients[index].password != "wrong"


def test_login_with_unknown_username_is_not_found(accounts_file):
    clients = make_list(accounts_file, "alice", "bob")
    assert clients.find(Client("nobody")) == (False, -1)


def test_delete_client(accounts_file):
    clients = make_list(accounts_file, "alice", "bob", "carol")
    assert clients.delete_client(Client("bob"))
    assert not clients.delete_client(Client("bob"))
    assert usernames(ClientList(str(accounts_file)).clients) == ["alice", "carol"]


# --- Recursive binary search -----------------------------------------------------

NAMES = ["alice", "bob", "carol", "dave", "erin", "frank", "gina"]


@pytest.mark.parametrize("size", range(1, len(NAMES) + 1))
def test_binary_search_finds_every_client(accounts_file, size):
    clients = make_list(accounts_file, *NAMES[:size])
    for expected_index, name in enumerate(NAMES[:size]):
        assert clients.find(Client(name)) == (True, expected_index)


@pytest.mark.parametrize("missing", ["aaron", "bobby", "zed", "", "Alice"])
def test_binary_search_reports_missing_clients(accounts_file, missing):
    clients = make_list(accounts_file, *NAMES)
    assert clients.find(Client(missing)) == (False, -1)


def test_binary_search_on_empty_list(accounts_file):
    clients = ClientList(str(accounts_file))
    assert clients.find(Client("alice")) == (False, -1)


# --- Leaderboard -----------------------------------------------------------------

def test_leaderboard_is_ordered_by_highest_score(accounts_file):
    write_lines(
        accounts_file,
        "alice,pw,Q?,A,0,50",
        "bob,pw,Q?,A,0,300",
        "carol,pw,Q?,A,0,10",
        "dave,pw,Q?,A,0,120",
    )
    clients = ClientList(str(accounts_file))
    board = clients.sorted_by_score()
    assert usernames(board) == ["bob", "dave", "alice", "carol"]
    # the main list must stay sorted by username so the binary search keeps working
    assert usernames(clients.clients) == ["alice", "bob", "carol", "dave"]


def test_leaderboard_ties_keep_alphabetical_order(accounts_file):
    write_lines(accounts_file, "zoe,pw,Q?,A,0,100", "amy,pw,Q?,A,0,100", "max,pw,Q?,A,0,200")
    board = ClientList(str(accounts_file)).sorted_by_score()
    assert usernames(board) == ["max", "amy", "zoe"]


def test_top_players_returns_at_most_five(accounts_file):
    write_lines(accounts_file, *(f"p{i},pw,Q?,A,0,{i * 10}" for i in range(8)))
    top = ClientList(str(accounts_file)).top_players(5)
    assert usernames(top) == ["p7", "p6", "p5", "p4", "p3"]


def test_new_score_only_replaces_highest_score_when_better(accounts_file):
    write_lines(accounts_file, "alice,pw,Q?,A,0,100")
    clients = ClientList(str(accounts_file))

    clients.update_player_in_list(Client("alice", score=60))
    alice = ClientList(str(accounts_file)).clients[0]
    assert (alice.score, alice.highest_score) == (60, 100)

    clients.update_player_in_list(Client("alice", score=250))
    alice = ClientList(str(accounts_file)).clients[0]
    assert (alice.score, alice.highest_score) == (250, 250)


def test_updating_unknown_player_does_nothing(accounts_file):
    clients = make_list(accounts_file, "alice")
    assert not clients.update_player_in_list(Client("nobody", score=999))
