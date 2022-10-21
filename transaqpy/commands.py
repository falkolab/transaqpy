from dataclasses import dataclass, asdict
from enum import auto, IntEnum, Enum
from typing import List, Union, Literal, Optional
from datetime import datetime, timedelta

from transaqpy import TransaqException
from transaqpy.utils import CommandMaker, TRANSAQ_DATETIME_FORMAT

try:
    from enum import StrEnum
except ImportError as err:
    class StrEnum(str, Enum):
        pass


def connect(login: str, password: str,
            host: str = 'localhost',
            port: int = 3939,
            rqdelay: int = 100,
            micex_registers: bool = True,
            push_u_limits: int = 10,
            push_pos_equity: int = 10,
            utc_time: bool = False,
            language: str = 'ru',
            autopos: bool = None,
            proxy: str = None,
            session_timeout: str = None,
            request_timeout: str = None,
            milliseconds: bool = None
            ) -> CommandMaker:
    mk = CommandMaker("connect").add({
        "login": login,
        "password": password,
        "host": host,
        "port": str(port),
        "utc_time": str(utc_time).lower(),
        'language': language
    })
    if micex_registers:
        mk.add({
            "micex_registers": "true",
            "rqdelay": str(rqdelay)
        })
    if autopos is not None:
        mk.add('autopos', str(autopos).lower())
    if push_u_limits > 0:
        mk.add("push_u_limits", str(push_u_limits))
    if push_pos_equity > 0:
        mk.add("push_pos_equity", str(push_pos_equity))
    if proxy is not None:
        mk.add('proxy', proxy)
    if session_timeout is not None:
        mk.add('session_timeout', str(session_timeout))
    if request_timeout is not None:
        mk.add('request_timeout', str(request_timeout))
    if milliseconds is not None:
        mk.add('milliseconds', str(milliseconds).lower())
    return mk


@dataclass(frozen=True)
class Ticker:
    """
       Args:
        board (str): Идентификатор режима торгов.
        seccode (str): Код инструмента.
    """
    board: str
    seccode: str

    @property
    def id(self):
        return "{0}-{1}".format(self.board, self.seccode)

    def __str__(self):
        return "Board: {0}, Security Code: {1}".format(self.board, self.seccode)

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.id == other.id


def get_history_data(ticker: Ticker, period: int, count: int, reset: bool = True) -> CommandMaker:
    """
    Выдать последние N свечей заданного периода, по заданному инструменту.

    :param ticker:
        Идентификатор режима торгов, Код инструмента.
    :param period:
        Идентификатор периода.
    :param count:
        Количество свечей.
    :param reset:
        Параметр reset="true" говорит,
        что нужно выдавать самые свежие данные,
        в противном случае будут выданы свечи
        в продолжение предыдущего запроса.
    :return:
        Результат отправки команды.
    """
    return CommandMaker("gethistorydata") \
        .add('security', asdict(ticker)) \
        .add('period', str(period)) \
        .add('count', str(count)) \
        .add('reset', str(reset).lower())


@dataclass(frozen=True)
class TickerTradeLimited(Ticker):
    tradeno: int

    @classmethod
    def from_ticker(cls, ticker: Ticker, tradeno: int):
        return TickerTradeLimited(ticker.board, ticker.seccode, tradeno)


def subsctibe_ticks_many(tickers: List[TickerTradeLimited], filter_=False) -> CommandMaker:
    mk = CommandMaker("subscribe_ticks")
    for ticker in tickers:
        mk.add('security', asdict(ticker))
        mk.add('filter', str(filter_).lower())
    return mk


def subscribe_ticks(ticker: TickerTradeLimited = None, filter_=False) -> CommandMaker:
    return subsctibe_ticks_many([] if ticker is None else [ticker], filter_)


class SubscriptionEntity(StrEnum):
    ALL_TRADES = 'alltrades'
    QUOTATIONS = 'quotations'
    BID_ASK = 'quotes'


def __subscribe_helper(command_name: str, _type: SubscriptionEntity, tickers: List[Ticker]) -> CommandMaker:
    mk = CommandMaker(command_name)
    t = CommandMaker(tag=_type.value, parent=mk.root)
    for ticker in tickers:
        t.add('security', asdict(ticker))
    return mk


def subscribe(_type: SubscriptionEntity, tickers: List[Ticker]) -> CommandMaker:
    return __subscribe_helper('subscribe', _type, tickers)


def unsubscribe(_type: SubscriptionEntity, tickers: List[Ticker]) -> CommandMaker:
    return __subscribe_helper('unsubscribe', _type, tickers)


class BuySellAction(StrEnum):
    BUY = 'B'
    SELL = 'S'


class OrderUnfilled(StrEnum):
    PUT_IN_QUEUE = 'PutInQueue',
    FOK = auto()
    IOC = auto()


def new_order(ticker: Ticker, client: str,
              buysell: BuySellAction,
              quantity: int,
              price: float = 0,
              union: str = None,
              bymarket: bool = None,
              usecredit: bool = True,
              unfilled: OrderUnfilled = OrderUnfilled.PUT_IN_QUEUE,
              nosplit: bool = False) -> CommandMaker:
    mk = CommandMaker('neworder')
    mk.add('security', asdict(ticker))
    mk.add('client', client)
    if union:
        mk.add("union", union)
    mk.add('buysell', buysell.value)
    mk.add('quantity', str(quantity))
    mk.add('unfilled', unfilled.value)
    if not price and bymarket is None:
        bymarket = True
    if not bymarket:
        mk.add('price', str(price))
    if bymarket:
        mk.add('bymarket')
    if usecredit:
        mk.add('usecredit')
    if nosplit:
        mk.add('nosplit')
    return mk


def _ensure_percentage(value: str):
    pair = value.split('%')
    try:
        _ = len(pair) == 2 and 0 <= float(pair[0]) <= 100.0
        if not _:
            raise ValueError
    except (IndexError, ValueError):
        raise TransaqException('Should be valid percentage value')


class StopOrderType(StrEnum):
    STOP_LOSS = 'stoploss'
    TAKE_PROFIT = 'takeprofit'


def new_sl_tp_order(
        ticker: Ticker,
        buysell: BuySellAction,
        client: str = None,
        union: str = None,
        expdate: datetime = None,
        linkedorderno: str = None,
        validfor: Union[Literal[0, 'till_canceled'], datetime] = None,

        sl_activationprice: float = None,
        sl_orderprice: float = None,
        sl_bymarket: bool = None,
        sl_quantity: Union[int, str] = None,
        sl_usecredit: bool = True,
        sl_guardtime: Optional[int] = None,  # sec
        sl_brokerref: Optional[str] = None,

        tp_activationprice: float = None,
        tp_quantity: Union[int, str] = 0,
        tp_usecredit: bool = True,
        tp_guardtime: Optional[timedelta] = None,
        tp_brokerref: Optional[str] = None,
        tp_correction: Union[float, str] = None,
        tp_spread: Union[float, str] = None,
        tp_bymarket: bool = None,
) -> CommandMaker:
    mk = CommandMaker('newstoporder')
    mk.add('security', asdict(ticker))
    if client:
        mk.add('client', client)
    if union:
        mk.add("union", union)
    mk.add('buysell', buysell.value)
    if linkedorderno:
        mk.add('linkedorderno', str(linkedorderno))
    if validfor is not None:
        if isinstance(validfor, datetime):
            mk.add('validfor', validfor.strftime(TRANSAQ_DATETIME_FORMAT))
        else:
            mk.add('validfor', str(validfor))
    if expdate:
        mk.add('expdate', expdate.strftime(TRANSAQ_DATETIME_FORMAT))

    if sl_quantity:
        sl = CommandMaker(tag='stoploss', parent=mk.root)
        quantity: Union[int, str] = sl_quantity
        if quantity:
            if not isinstance(quantity, int):
                _ensure_percentage(quantity)
            sl.add('quantity', str(quantity))
        sl.add('activationprice', str(sl_activationprice))
        if sl_bymarket:
            sl.add('bymarket')
        else:
            sl.add('orderprice', str(sl_orderprice))
        if sl_usecredit:
            sl.add('usecredit')
        if sl_brokerref:
            sl.add('brokerref', sl_brokerref)
        if sl_guardtime:
            sl.add('guardtime', str(sl_guardtime))

    if tp_quantity:
        tp = CommandMaker(tag='takeprofit', parent=mk.root)
        quantity: Union[int, str] = tp_quantity
        if quantity:
            if not isinstance(quantity, int):
                _ensure_percentage(quantity)
            tp.add('quantity', str(quantity))
        tp.add('activationprice', str(tp_activationprice))
        if tp_bymarket:
            tp.add('bymarket')
        if tp_usecredit:
            tp.add('usecredit')
        if tp_brokerref:
            tp.add('brokerref', tp_brokerref)
        if tp_guardtime:
            tp.add('guardtime', str(tp_guardtime))

        correction: Union[float, str] = tp_correction
        if correction:
            if not isinstance(correction, float):
                _ensure_percentage(correction)
            tp.add('correction', str(correction))

        spread: Union[float, str] = tp_spread
        if spread:
            if not isinstance(spread, float):
                _ensure_percentage(spread)
            tp.add('spread', str(spread))

    return mk


def cancel_order(transaction_id) -> CommandMaker:
    return CommandMaker('cancelorder').add('transactionid', str(transaction_id))


def cancel_stoporder(transaction_id) -> CommandMaker:
    return CommandMaker('cancelstoporder').add('transactionid', str(transaction_id))


class ConditionOrderType(StrEnum):
    """
    BID = лучшая цена покупки
    BID_OR_LAST = лучшая цена покупки или сделка по заданной цене и выше
    ASK = лучшая цена продажи
    ASK_OR_LAST = лучшая цена продажи или сделка по заданной цене и ниже
    TIME = время выставления заявки на Биржу
    COV_DOWN = обеспеченность ниже заданной
    COV_UP = обеспеченность выше заданной
    LAST_UP = сделка на рынке по заданной цене или выше
    LAST_DOWN = сделка на рынке по заданной цене или ниже
    """
    BID = 'Bid'
    BID_OR_LAST = 'BidOrLast'
    ASK = 'Ask'
    ASK_OR_LAST = 'AskOrLast'
    TIME = 'Time'
    COV_DOWN = 'CovDown'
    COV_UP = 'CovUp'
    LAST_UP = 'LastUp'
    LAST_DOWN = 'LastDown'


def new_conditional_order(ticker: Ticker, client: str, buysell: BuySellAction, quantity: int, price: float,
                          union: str,
                          cond_type: ConditionOrderType,
                          valid_before: Union[Literal[0, 'till_canceled'], datetime],
                          valid_after: Union[Literal[0], datetime],
                          cond_value: Union[float, datetime] = None,
                          hidden: int = None,
                          bymarket: bool = True,
                          usecredit: bool = True,
                          brokerref: str = None,
                          nosplit: bool = False,
                          within_pos: bool = False,
                          expdate: datetime = None) -> CommandMaker:
    mk = CommandMaker('newcondorder')
    mk.add('security', asdict(ticker))
    mk.add('client', client)
    mk.add("union", union)
    if hidden is not None:
        mk.add('hidden', str(hidden))
    mk.add('quantity', str(quantity))
    mk.add('buysell', buysell.value)
    if not bymarket:
        mk.add('price', str(price))
    else:
        mk.add('bymarket')
    if brokerref is not None:
        mk.add('brokerref')

    if valid_before is not None:
        if isinstance(valid_before, datetime):
            mk.add('valid_before', valid_before.strftime(TRANSAQ_DATETIME_FORMAT))
        else:
            mk.add('valid_before', str(valid_before))

    if valid_after is not None:
        if isinstance(valid_after, datetime):
            mk.add('valid_after', valid_after.strftime(TRANSAQ_DATETIME_FORMAT))
        else:
            mk.add('valid_after', str(valid_after))

    if usecredit:
        mk.add('usecredit')
    if nosplit:
        mk.add('nosplit')
    if within_pos:
        mk.add('within_pos')

    if expdate is not None:
        mk.add('expdate', expdate.strftime(TRANSAQ_DATETIME_FORMAT))

    mk.add('cond_type', cond_type.value)
    if cond_value is not None:
        if isinstance(cond_value, datetime):
            mk.add('cond_value', cond_value.strftime(TRANSAQ_DATETIME_FORMAT))
        else:
            mk.add('cond_value', str(cond_value))
    return mk


def get_forts_positions(client: str = None) -> CommandMaker:
    if client is None:
        return CommandMaker('get_forts_positions')
    else:
        return CommandMaker('get_forts_positions', client=client)


def get_client_limits(client: str) -> CommandMaker:
    return CommandMaker('get_client_limits', client=client)


def get_sec_info(market: str, security_code: str) -> CommandMaker:
    mk = CommandMaker('get_securities_info')
    return mk.add('security', {
        'market': market,
        'seccode': security_code
    })


class OrderMoveType(IntEnum):
    """
    0: не менять количество;
    1: изменить количество;
    2: при несовпадении количества с текущим – снять заявку.
    """
    DO_NOT_CHANGE_QUANTITY = 0
    DO_CHANGE_QUANTITY = 1
    WITHDRAW_ON_NOT_COINCIDENCE = 2


def move_order(transaction_id: str, price: float, quantity: int = 0,
               moveflag: OrderMoveType = OrderMoveType.DO_NOT_CHANGE_QUANTITY) -> CommandMaker:
    mk = CommandMaker('moveorder')
    mk.add('transactionid', str(transaction_id))
    mk.add('price', str(price))
    mk.add('quantity', str(quantity))
    mk.add('moveflag', str(moveflag.value))
    return mk


def get_united_equity(union: str) -> CommandMaker:
    """
    Получить актуальную оценку ликвидационной стоимости Единого портфеля,
    соответствующего юниону.
    """
    return CommandMaker('get_united_equity', union=union)


def get_united_collateral(union: str) -> CommandMaker:
    """
    Получить размер средств, заблокированных биржей (FORTS) под срочные
    позиции клиентов юниона
    """
    return CommandMaker('get_united_go', union=union)


def get_mc_portfolio(client: str = None, union: str = None,
                     currency: Optional[bool] = None,
                     asset: Optional[bool] = None,
                     money: Optional[bool] = None,
                     depo: Optional[bool] = None,
                     registers: Optional[bool] = None,
                     maxbs: Optional[bool] = None) -> CommandMaker:
    """
    Получить мультивалютный портфель.
    В команде необходимо задать только один из параметров (client или union).
    :param client:
    :param union:
    :param currency:
    :param asset:
    :param money:
    :param depo:
    :param registers:
    :param maxbs:
    :return:
    """
    if client is None and union is None:
        raise ValueError("please specify client OR union")
    keys = list(filter(lambda x: x != "return", get_mc_portfolio.__annotations__))
    loc = locals()
    kw = {key: loc[key] for key in keys if loc[key] is not None}
    return CommandMaker('get_mc_portfolio', **kw)


def get_max_buy_sell(client: str = None, union: str = None, tickers: List[Ticker] = []):
    """
    Получение информации о максимально возможных объемах заявок на покупку и на продажу по перечисленным бумагам для заданного клиента или юниона
    :param client:
    :param union:
    :param tickers:
    :return:
    """
    mk = CommandMaker('get_max_buy_sell', client=client, union=union)

    for ticker in tickers:
        mk.add('security', asdict(ticker))
    return mk
