![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000355_1cc3c05d39bf6fa98e195a4ec1966dc0716058e706674d93425c9d1d547342bd.png)

Phương thức `publishNotifications()` sử dụng `messageProducer()` để đảm bảo `exchange` (thành phần định tuyến thông điệp trong RabbitMQ) tồn tại, sau đó lấy thể hiện (instance) của `MessageProducer` (đối tượng sản sinh thông điệp) dùng để xuất bản. RabbitMQ hỗ trợ tính lũy thỏa (`exchange idempotence` - tính chất tạo lập nhiều lần vẫn cho kết quả như lần đầu), vì vậy trong lần đầu tiên bạn yêu cầu, exchange sẽ được khởi tạo, còn ở tất cả các lần tiếp theo bạn sẽ nhận lại exchange đã tồn tại từ trước đó. Chúng tôi không duy trì một instance mở sẵn của `MessageProducer` nhằm phòng ngừa trường hợp phát sinh sự cố với `channel` (kênh truyền thông) của `broker` (máy chủ điều phối thông điệp) bên dưới. Việc tái lập kết nối mỗi khi thực thi thao tác xuất bản (`publish`) giúp ngăn ngừa nguy cơ bên phát hành (`publisher`) bị tê liệt hoàn toàn. Chúng ta có thể cần lưu ý tới các vấn đề tiềm ẩn về hiệu năng nếu việc liên tục kết nối lại trở thành nút thắt cổ chai (`bottleneck`). Tuy nhiên ở thời điểm hiện tại, chúng ta sẽ dựa vào khoảng thời gian tạm dừng (`pauses`) đã được cấu hình giữa các lần xuất bản để giảm tải chi phí phụ trội (`overhead`) do việc kết nối lại gây ra.

Nhắc đến khoảng thời gian tạm dừng giữa các lần xuất bản, không có đoạn mã nào ở phần trước chỉ ra cách các Event (`Domain Events` - sự kiện miền nghiệp vụ) được xuất bản tới exchange theo định kỳ và lặp lại. Việc này có thể được thực hiện theo vài cách khác nhau tùy thuộc vào môi trường vận hành của bạn. Một trong số đó là sử dụng `JMX TimerMBean` (thành phần quản lý tác vụ định kỳ trong Java Management Extensions) để quản trị các khoảng thời gian lặp lại.

Trước khi trình bày giải pháp bộ đếm thời gian (`timer`) dưới đây, cần lưu ý một bối cảnh quan trọng: Tiêu chuẩn Java MBean cũng sử dụng thuật ngữ `notification` (thông báo), nhưng khái niệm này không giống với notification trong tiến trình xuất bản sự kiện của chúng ta. Trong trường hợp của JMX, một trình lắng nghe (`listener`) sẽ nhận được thông báo mỗi khi bộ đếm thời gian kích hoạt. Bạn chỉ cần phân biệt rạch ròi hai khái niệm này trong đầu.

Bất kể khoảng thời gian phù hợp nào được xác định và cấu hình cho một timer nhất định, một `NotificationListener` (trình lắng nghe thông báo) sẽ được đăng ký để `MBeanServer` có thể phát thông báo mỗi khi chạm đến mốc thời gian định kỳ:

```java
mbeanServer.addNotificationListener(
    timer.getObjectName(),
    new NotificationListener() {
        public void handleNotification(
            Notification aTimerNotification,
            Object aHandback) {
            ApplicationServiceRegistry
                .notificationService()
                .publishNotifications();
        }
    },
    null,
    null);

```

Trong ví dụ này, khi phương thức `handleNotification()` được gọi do timer kích hoạt, nó yêu cầu `NotificationService` (dịch vụ thông báo) thực thi thao tác `publishNotifications()`. Đó là tất cả những gì cần thiết. Chừng nào `TimerMBean` còn tiếp tục kích hoạt theo các chu kỳ định kỳ, lặp lại, các Domain Event sẽ tiếp tục được xuất bản qua exchange và được tiêu thụ bởi các bên đăng ký (`subscribers` - các đối tượng đăng ký nhận tin) trên toàn hệ thống doanh nghiệp.

Việc sử dụng bộ đếm thời gian do máy chủ ứng dụng (`application server`) quản lý mang lại một lợi thế bổ sung: bạn không phải tự tạo một thành phần riêng để theo dõi vòng đời (`life cycle`) của tiến trình xuất bản. Chẳng hạn, nếu `publishNotifications()` vì lý do nào đó gặp sự cố trong một lượt thực thi và kết thúc bằng một ngoại lệ (`exception`), thì `TimerMBean` vẫn tiếp tục chạy và kích hoạt ở các chu kỳ tiếp theo. Quản trị viên có thể cần can thiệp xử lý các lỗi hạ tầng (có thể phát sinh từ RabbitMQ), nhưng một khi sự cố được giải quyết, các thông điệp sẽ lại tiếp tục được xuất bản bình thường. Ngoài ra, còn có các công cụ hẹn giờ khác sẵn có phục vụ mục đích này, ví dụ như [Quartz].

Tuy nhiên, chúng ta vẫn còn một câu hỏi bỏ ngỏ về việc khử trùng lặp thông điệp (`message de-duplication`). Khử trùng lặp thông điệp là gì? Và tại sao các subscriber trong hệ thống nhắn tin lại bắt buộc phải hỗ trợ cơ chế này?

Khử trùng lặp sự kiện (`Event De-duplication`) Khử trùng lặp là một đòi hỏi tất yếu trong các môi trường mà một thông điệp được xuất bản qua hệ thống nhắn tin có nguy cơ bị phân phối tới các subscriber nhiều hơn một lần. Có nhiều nguyên nhân dẫn tới việc trùng lặp thông điệp. Một kịch bản điển hình xảy ra như sau:

1. RabbitMQ phân phối các thông điệp mới gửi tới một hoặc nhiều subscriber.
2. Các subscriber xử lý những thông điệp này.
3. Trước khi subscriber kịp gửi tín hiệu xác nhận (`acknowledgement / ack`) rằng thông điệp đã được tiếp nhận và xử lý thành công, tiến trình của subscriber gặp sự cố và sập (`fail`).
4. RabbitMQ tiến hành phân phối lại các thông điệp chưa được xác nhận đó.

Khả năng này cũng xảy ra khi xuất bản dữ liệu lấy từ một Event Store (`Event Store` - kho lưu trữ sự kiện), trong bối cảnh hệ thống nhắn tin không dùng chung cơ chế lưu trữ bền vững (`persistence mechanism`) với Event Store, đồng thời không có các giao dịch toàn cục XA (`XA transactions` - chuẩn giao dịch phân tán hỗ trợ commit nguyên tử trên nhiều tài nguyên) để kiểm soát việc xác nhận nguyên tử (`atomic commits`) giữa các thay đổi của Event Store và hệ thống nhắn tin. Như đã thảo luận trước đây trong phần "Publishing Notifications through Messaging Middleware" (Xuất bản thông báo qua phần mềm trung gian nhắn tin), đó chính xác là tình huống mà chúng ta đang đối mặt. Hãy xem xét một kịch bản minh họa rõ nét cách một thông điệp có thể bị gửi nhiều lần:

1. `NotificationService` truy vấn và xuất bản 3 thể hiện `Notification` chưa được xuất bản. Nó cập nhật bản ghi theo dõi trạng thái này bằng `PublishedMessageTracker` (bộ theo dõi thông điệp đã xuất bản).
2. Broker của RabbitMQ tiếp nhận cả 3 thông điệp và chuẩn bị gửi chúng tới tất cả subscriber.
3. Tuy nhiên, do một điều kiện ngoại lệ nào đó trên máy chủ ứng dụng, `NotificationService` gặp sự cố. Thay đổi cập nhật trên `PublishedMessageTracker` không được commit (lưu thành công).

4. RabbitMQ phân phối các thông điệp mới gửi tới các subscriber.
5. Sự cố ngoại lệ trên application server được khắc phục. Tiến trình xuất bản bắt đầu lại từ đầu và `NotificationService` gửi thành công các thông điệp cho toàn bộ Event chưa được xuất bản. Điều này đồng nghĩa với việc gửi lại (thêm một lần nữa!) thông điệp cho tất cả Event đã từng được xuất bản trước đó nhưng chưa được ghi nhận vào `PublishedMessageTracker`.
6. RabbitMQ phân phối các thông điệp mới gửi tới các subscriber, trong đó có ít nhất 3 thông điệp bị phân phối lặp lại.

Trong kịch bản này, tôi lấy con số 3 Event một cách ngẫu nhiên để làm ví dụ. Tôi hoàn toàn có thể lấy một, hai, bốn hoặc nhiều hơn thế. Số lượng không quan trọng, điều cốt lõi là những sự cố như vậy hoàn toàn có thể gây ra việc gửi lại thông điệp. Khi đối mặt với tình huống này cũng như các nguyên nhân gây trùng lặp thông điệp khác, việc khử trùng lặp là bắt buộc. Bạn có thể tham khảo mẫu thiết kế Idempotent Receiver (`Idempotent Receiver` - bộ nhận lũy thỏa) trong tài liệu của [Hohpe & Woolf] để tìm hiểu sâu hơn về giải pháp xử lý.

## An Idempotent Operation

Một thao tác lũy thỏa (`idempotent operation`) là thao tác có thể được thực thi liên tiếp từ hai hay nhiều lần mà vẫn đem lại kết quả hoàn toàn đồng nhất như khi chỉ thực thi đúng một lần duy nhất.

Một phương án để đối phó với nguy cơ phân phối trùng lặp thông điệp là thiết kế thao tác mô hình của subscriber đạt tính lũy thỏa. Khi đó, phản ứng của subscriber đối với mọi thông điệp đều là các thao tác lũy thỏa tác động lên chính domain model (`domain model` - mô hình miền nghiệp vụ) của nó. Vấn đề nằm ở chỗ: thiết kế một đối tượng miền (hoặc bất kỳ đối tượng nào) có tính lũy thỏa là một việc rất khó khăn, thiếu thực tế hoặc thậm chí bất khả thi. Và nếu cố gắng thiết kế bản thân Event mang theo thông tin thể hiện một hành động lũy thỏa cần thực hiện, điều đó cũng có thể gây phiền toái. Thứ nhất, bên gửi phải hiểu tường tận tình trạng nghiệp vụ hiện thời của tất cả bên nhận tương ứng với trạng thái Event mà họ chuẩn bị phát đi. Hơn nữa, việc tiếp nhận các Event bị sai lệch thứ tự do độ trễ mạng (`latency`), cơ chế thử lại (`retries`), v.v., hoàn toàn có thể gây ra lỗi sai lệch dữ liệu.

Khi tính lũy thỏa của đối tượng miền không phải là giải pháp khả thi, bạn có thể chuyển sang thiết kế chính bản thân subscriber/receiver đạt tính lũy thỏa. Receiver có thể được lập trình để từ chối thực thi thao tác nếu phát hiện thông điệp đó bị trùng lặp. Trước hết, bạn nên kiểm tra xem sản phẩm nhắn tin (`messaging product`) của mình có hỗ trợ tính năng này sẵn hay không. Nếu không, receiver của bạn sẽ phải tự theo dõi xem những thông điệp nào đã từng được xử lý. Một phương pháp để thực hiện điều đó là cấp phát một vùng lưu trữ trong cơ chế lưu trữ bền vững của subscriber để lưu tên của topic/exchange cùng với ID định danh duy nhất của tất cả thông điệp đã xử lý — đúng vậy, cách làm này tương tự như một `PublishedMessageTracker`. Sau đó, bạn có thể truy vấn kiểm tra trùng lặp trước khi xử lý từng thông điệp. Nếu câu truy vấn phát hiện thông điệp đã được xử lý từ trước, subscriber chỉ việc bỏ qua nó. Việc theo dõi thông điệp đã xử lý không thuộc về domain model. Nó chỉ nên được xem như một giải pháp kỹ thuật tình thế nhằm xử lý các đặc thù thường gặp trong kiến trúc nhắn tin.

Khi sử dụng một sản phẩm phần mềm trung gian nhắn tin (`messaging middleware`) thông thường, việc chỉ lưu lại bản ghi của thông điệp được xử lý gần đây nhất là không đủ, bởi thông điệp có thể được tiếp nhận không đúng thứ tự ban đầu (`out of order`). Do đó, một truy vấn khử trùng lặp dựa trên điều kiện ID thông điệp nhỏ hơn ID gần nhất sẽ khiến bạn vô tình bỏ qua những thông điệp thực chất đến muộn do sai lệch thứ tự. Một điểm khác cũng cần cân nhắc là đôi khi bạn sẽ muốn dọn dẹp và hủy bỏ các bản ghi theo dõi thông điệp đã quá cũ, tương tự như cơ chế dọn rác (`garbage collection`) trong cơ sở dữ liệu.

Khi áp dụng phương thức thông báo dựa trên REST (`REST-based notification`), việc khử trùng lặp thực tế không còn là vấn đề nan giải. Phía client tiếp nhận chỉ cần lưu trữ duy nhất định danh của thông báo được áp dụng gần đây nhất, bởi vì chúng sẽ luôn chỉ áp dụng những thông báo của các sự kiện diễn ra sau mốc thời gian đó. Mỗi nhật ký thông báo (`notification log`) sẽ luôn được sắp xếp theo thứ tự thời gian đảo ngược (giảm dần) dựa theo định danh của thông báo.

Trong cả hai trường hợp — dù là subscriber dùng messaging middleware hay client nhận thông báo qua REST — điều quan trọng là việc lưu vết định danh thông điệp đã xử lý phải được commit đồng thời cùng mọi thay đổi về trạng thái của domain model cục bộ. Nếu không làm vậy, bạn sẽ không thể duy trì được tính nhất quán trong việc theo dõi đồng hành với những sửa đổi được thực hiện để phản hồi lại các Event.

## Wrap-Up

Trong chương này, chúng ta đã xem xét định nghĩa về Domain Event và cách chúng giúp xác định thời điểm việc mô hình hóa một Event sẽ mang lại lợi thế cho thiết kế của bạn.

* Bạn đã nắm được Domain Event là gì, cũng như thời điểm và lý do tại sao nên sử dụng chúng.
* Bạn đã tìm hiểu cách mô hình hóa các Event dưới dạng đối tượng, và trường hợp nào chúng bắt buộc phải được định danh duy nhất.
* Bạn đã cân nhắc khi nào một Event nên mang các đặc tính của một Aggregate (`Aggregate` - cụm đối tượng gồm các Entity và Value Object có cùng ranh giới nhất quán), và khi nào một Event đơn giản dạng Value Object lại phát huy hiệu quả tốt nhất.
* Bạn đã thấy cách các thành phần Xuất bản - Đăng ký (`Publish-Subscribe`) gọn nhẹ được vận dụng bên trong mô hình.

* Bạn đã khám phá những thành phần nào đóng vai trò xuất bản Event và những thành phần nào đăng ký nhận chúng.
* Bạn đã hiểu lý do tại sao cần xây dựng một Event Store, cách triển khai cũng như cách thức vận hành của nó trong thực tế.
* Bạn đã nắm bắt hai cách tiếp cận để xuất bản Event ra bên ngoài Bounded Context (`Bounded Context` - ngữ cảnh giới hạn phân định biên giới mô hình): thông báo qua REST và sử dụng messaging middleware.
* Bạn đã học được một số phương pháp để khử trùng lặp thông điệp bên trong các hệ thống tiếp nhận đăng ký.

Tiếp theo, chúng ta sẽ chuyển hướng đáng kể để tìm hiểu sâu hơn về cách sắp xếp, tổ chức các đối tượng trong domain model một cách khoa học bằng việc sử dụng Module.

## Chapter 9

## Modules

Bí quyết của mọi thắng lợi nằm ở sự tổ chức những điều không hiển hiện. — Marcus Aurelius

Nếu đang làm việc với Java hoặc C#, bạn ắt hẳn đã quá quen thuộc với Module (`Module` - đơn vị đóng gói cấu trúc mã nguồn), dẫu có thể bạn biết đến chúng dưới những tên gọi khác. Java gọi chúng là `package`. C# gọi chúng là `namespace`. Thực tế trong Ruby, bạn có thể sử dụng cấu trúc ngôn ngữ `module` để tạo ra namespace cho các lớp (`class`). Trong trường hợp của Ruby, tên mẫu hình DDD trùng khớp hoàn toàn với cấu trúc ngôn ngữ. Để phù hợp với ngữ cảnh DDD xuyên suốt cuốn sách, tôi sẽ tiếp tục gọi chúng là Module trong hầu hết các trường hợp. Bạn sẽ rất dễ dàng ánh xạ tên gọi này sang thuật ngữ ngôn ngữ lập trình mà bạn sử dụng thường ngày. Tôi sẽ không dành nhiều thời gian để giải thích về mặt kỹ thuật Module làm được những gì, bởi có lẽ bạn đã hiểu rõ điều đó từ lâu.

## Road Map to This Chapter

* Nắm bắt sự khác biệt giữa Module truyền thống và phương pháp tiếp cận mô-đun hóa trong triển khai (`deployment modularity`) hiện đại hơn.
* Cân nhắc tầm quan trọng của việc đặt tên Module theo Ngôn ngữ Chung (`Ubiquitous Language` (1) - ngôn ngữ thống nhất giữa chuyên gia nghiệp vụ và đội ngũ phát triển).
* Nhận thấy việc thiết kế Module một cách máy móc thực chất sẽ bóp nghẹt tính sáng tạo khi xây dựng mô hình như thế nào.
* Tìm hiểu các quyết định thiết kế và sự đánh đổi mà các nhóm phát triển tại SaaSOvation đã thực hiện.
* Khám phá vai trò của Module bên ngoài phạm vi domain model, và thời điểm nên ưu tiên tạo Module mới thay vì chia tách thành các Bounded Context mới.

## Designing with Modules

Trong ngữ cảnh DDD, các Module trong mô hình đóng vai trò là những thùng chứa có tên gọi dành cho các lớp đối tượng miền có tính gắn kết nội tại cao (`high cohesion`) với nhau. Mục tiêu hướng tới là giảm thiểu tối đa mức độ phụ thuộc (`low coupling`) giữa các lớp nằm ở các Module khác nhau. Vì Module trong DDD không phải là những ngăn chứa đồ chung chung hay vô hồn, nên việc đặt tên chuẩn xác cho chúng là cực kỳ quan trọng. Tên của chúng là một khía cạnh trọng yếu cấu thành nên Ubiquitous Language.

> Hãy lựa chọn các Module sao cho chúng kể được câu chuyện của hệ thống và chứa đựng một tập hợp các khái niệm có tính gắn kết chặt chẽ. Cách tiếp cận này thường mang lại mức độ phụ thuộc thấp giữa các Module, nhưng nếu không đạt được điều đó, hãy tìm cách thay đổi mô hình để tách bạch các khái niệm... Hãy đặt cho các Module những cái tên trở thành một phần của Ubiquitous Language. Module và tên gọi của chúng phải phản ánh được sự thấu hiểu sâu sắc đối với miền nghiệp vụ. [Evans, tr. 110, 111]

Có một vài quy tắc đơn giản cần ghi nhớ khi thiết kế Module, như được trình bày trong Bảng 9.1.

Bảng 9.1 Các quy tắc đơn giản khi thiết kế Module

| Những điều NÊN và KHÔNG NÊN làm với Module | Tại sao? |
| --- | --- |
| **NÊN** thiết kế Module khớp với các khái niệm mô hình hóa. | Thông thường bạn sẽ có một Module dành cho một hoặc một vài Aggregate (10) có tính gắn kết với nhau, dù chỉ là gắn kết qua tham chiếu. |
| **NÊN** đặt tên Module theo Ubiquitous Language. | Đây là mục tiêu cơ bản của DDD, nhưng nó cũng sẽ diễn ra một cách hết sức tự nhiên nếu bạn tư duy đúng về các khái niệm đang được mô hình hóa. |
| **KHÔNG NÊN** tạo Module một cách máy móc dựa trên loại thành phần chung chung hoặc mẫu hình kỹ thuật đang dùng trong mô hình. | Mô hình của chúng ta hoàn toàn không thu được lợi ích gì nếu ta cô lập toàn bộ Aggregate vào một Module, gom toàn bộ Service (7) vào một Module khác, và dồn toàn bộ Factory (11) sang một Module tiếp theo. Làm như vậy là đi ngược lại mục đích của Module trong DDD, đồng thời có xu hướng bóp nghẹt khả năng sáng tạo hướng tới một mô hình phong phú. Thay vì suy nghĩ cởi mở về miền nghiệp vụ, bạn lại có xu hướng chỉ chăm chăm nghĩ về các loại thành phần hoặc mẫu thiết kế dùng để giải quyết bài toán trước mắt. |
| **NÊN** thiết kế các Module có tính kết nối lỏng lẻo (`loosely coupled`). | Việc đảm bảo các Module độc lập tối đa với nhau mang lại những lợi ích tương tự như việc giảm phụ thuộc giữa các lớp. Điều này giúp bạn dễ dàng bảo trì và tái cấu trúc (`refactor`) các khái niệm trong mô hình, đồng thời thuận lợi khi sử dụng các công cụ mô-đun hóa ở mức hạt lớn hơn như OSGi và Jigsaw. |
| **NÊN** nỗ lực hướng tới các quan hệ phụ thuộc không chu trình (`acyclic dependencies`) giữa các Module đồng cấp khi bắt buộc phải có sự liên kết. (Các Module đồng cấp là các module ở cùng một "cấp độ", hoặc có trọng lượng/tầm ảnh hưởng tương đương nhau trong thiết kế.) | Hiếm khi hoặc thậm chí phi thực tế để các Module hoàn toàn độc lập với nhau. Rốt cuộc, một domain model luôn hàm chứa sự liên kết nhất định. Tuy nhiên, bạn sẽ giảm bớt sự phụ thuộc giữa các thành phần nếu tư duy theo hướng biến quan hệ phụ thuộc giữa hai Module đồng cấp thành quan hệ đơn hướng (ví dụ: product phụ thuộc vào team, nhưng team không phụ thuộc vào product). |
| **NÊN** nới lỏng quy tắc một chút giữa Module cha và Module con. (Module cha nằm ở cấp cao hơn, còn Module con nằm ngay dưới một cấp — ví dụ: `parent.child`.) | Thực sự rất khó để ngăn chặn hoàn toàn sự phụ thuộc qua lại giữa Module cha và con. Nếu có thể, hãy nỗ lực duy trì các phụ thuộc phi chu trình giữa cha và con, nhưng hãy chấp nhận sự phụ thuộc vòng tròn (`circular dependencies`) nếu không còn cách nào khác để tránh (ví dụ: cha tạo ra con, và con phải tham chiếu ngược lại cha, dù chỉ qua định danh). |

Bảng 9.1 Các quy tắc đơn giản khi thiết kế Module (Tiếp theo)

| Những điều NÊN và KHÔNG NÊN làm với Module | Tại sao? |
| --- | --- |
| **KHÔNG NÊN** xem Module là một khái niệm tĩnh tại của mô hình, mà hãy để chúng được uốn nắn linh hoạt song hành cùng các đối tượng mà chúng tổ chức. | Nếu các khái niệm của mô hình luôn biến chuyển, thay đổi hình dạng, hành vi và tên gọi theo thời gian, thì rất có thể các Module tổ chức các khái niệm đó cũng cần được tạo mới, đổi tên hoặc xóa bỏ tương ứng. Đây không phải điều bắt buộc tuyệt đối trong mọi tình huống, nhưng nếu bạn nhận thấy tên gọi không còn ăn khớp, hãy refactor. Đúng vậy, việc này có thể gây phiền toái đôi chút, nhưng cái giá phải trả vẫn nhẹ nhàng hơn nhiều so với việc phải gánh chịu hậu quả từ những Module đặt tên sai lệch. |

Hãy coi Module như những "công dân hạng nhất" (`first-class citizens`) của mô hình, và nỗ lực tạo ra chúng với ý nghĩa trọn vẹn cùng sự cân nhắc kỹ lưỡng về tên gọi, tương đương với mức độ đầu tư dành cho Entity (5) (`Entity` - thực thể có danh tính định danh), Value Object (6) (`Value Object` - đối tượng giá trị không có định danh vòng đời), Service, và Event (8). Điều này đồng nghĩa với việc bạn phải đủ quyết đoán để đổi tên các Module hiện có với sự tự tin như khi tạo mới. Hãy luôn chủ động đặt các khái niệm miền mới mẻ hoặc vừa được làm mới vào các Module tương ứng đúng như những thấu hiểu nghiệp vụ cập nhật đòi hỏi.

Chẳng ai trong chúng ta cảm thấy dễ chịu khi mở ngăn kéo trong căn bếp gia đình và bắt gặp một mớ hỗn độn vô tổ chức gồm nĩa, dao, thìa, cờ-lê, tua-vít, đầu tuýp và búa trộn lẫn vào nhau. Rất có thể chúng ta sẽ từ chối dùng bữa với bộ dao thìa nĩa đó, ngay cả khi gom đủ một bộ đồ ăn hoàn chỉnh. Chúng ta cũng sẽ ngại bới móc ngăn kéo lộn xộn để tìm một chiếc tua-vít cụ thể chỉ vì sợ bị đứt tay bởi một con dao chặt thịt khuất lấp bên dưới.

Ngược lại, hãy hình dung một ngăn kéo nhà bếp nơi dao kéo ăn uống được sắp xếp gọn gàng thành từng bộ nĩa, dao, thìa; cùng với một hộp đồ nghề trong gara nơi mỗi loại công cụ đều có ngăn chứa ngăn nắp riêng biệt. Chúng ta sẽ chẳng gặp khó khăn gì khi tìm kiếm thứ cần dùng cho một mục đích cụ thể, cũng không chút ngần ngại đưa chúng vào đúng công năng. Mọi thứ đều được tổ chức khoa học, tinh tươm. Với sự sắp xếp ngăn nắp mang tính mô-đun hóa đó, không ai trông chờ sẽ tìm thấy tách và đĩa lót nằm chung ngăn kéo với dao thìa nĩa, mặc dù cả hai nhóm đều thuộc về nhà bếp. Những chồng bát đĩa gọn gàng sẽ tự nhiên khiến chúng ta tin rằng tách và đĩa lót có một vị trí thích hợp của riêng mình. Chỉ cần liếc nhanh qua các chạn bát gần đó, chúng sẽ nằm ngay ở đấy. Tương tự, ta cũng kỳ vọng dao kéo sắc nhọn được cất giữ ở nơi bảo vệ được lưỡi dao cũng như bảo vệ an toàn cho những người định sử dụng chúng.

Mặt khác, có lẽ chúng ta sẽ không sắp xếp đồ đạc trong bếp theo lối máy móc, chẳng hạn như dồn tất cả những đồ bền chắc vào một ngăn kéo và tống tất cả những món dễ vỡ lên chiếc tủ trên cao. Chúng ta không hề muốn phải ghi nhớ rằng bình hoa được cất chung với những chiếc tách trà sứ cao cấp chỉ vì cả hai đều có phần mong manh. Chúng ta cũng chẳng muốn phải nhớ rằng cây búa giã thịt bằng thép không gỉ được để cùng với dao kéo cao cấp chỉ vì cả hai món đồ bền bỉ này ít có nguy cơ làm hỏng nhau.

Nếu chúng ta mô hình hóa một căn bếp, việc xuất hiện một Module có tên `placesettings` (bộ đồ ăn) là hoàn toàn tự nhiên, và trong đó chúng ta sẽ thấy các đối tượng như `Fork` (nĩa), `Spoon` (thìa), và `Knife` (dao). Thậm chí, chúng ta có thể quyết định đặt cả `Serviette` (khăn ăn) vào đó, chứng minh rằng không phải cứ làm bằng kim loại thì mới đủ tiêu chuẩn trở thành một phần của Module `placesettings`. Mặt khác, việc mô hình hóa các bộ đồ ăn sẽ trở nên kém hữu ích nếu chúng ta lại chia thành các Module riêng biệt mang tên `pronged` (vật có răng cào), `scooping` (vật để múc), và `blunt` (vật có đầu tù).

Lưu ý rằng những tiến bộ gần đây trong việc mô-đun hóa phần mềm đã mang lại một cấp độ mô-đun hóa phần mềm khác biệt. Cách tiếp cận này liên quan đến việc đóng gói các phân đoạn phần mềm liên kết lỏng lẻo nhưng gắn kết chặt chẽ về mặt logic thành một đơn vị triển khai (`deployment unit`) theo từng phiên bản. Trong hệ sinh thái Java, chúng ta vẫn thường nghĩ về các tệp JAR, nhưng giờ đây chúng được lắp ráp theo phiên bản thông qua việc sử dụng các `OSGi bundle` hoặc các `module Java 8 Jigsaw`. Theo đó, nhiều module cấp cao, các phiên bản và mối phụ thuộc của chúng có thể được quản lý dưới dạng các bundle/module. Các loại module/bundle này có đôi chút khác biệt so với Module trong DDD, nhưng chúng có thể bổ trợ cho nhau. Rõ ràng, việc đóng gói các phần kết nối lỏng lẻo của một domain model vào các module có độ chi tiết thô hơn (`larger-grained modules`) dựa theo Module DDD là hoàn toàn hợp lý. Xét cho cùng, chính thiết kế liên kết lỏng lẻo của các Module DDD sẽ đóng góp trực tiếp vào khả năng đóng gói bằng OSGi hoặc mô-đun hóa sang Jigsaw của bạn.

## Cowboy Logic

* LB: "Cậu phải tự hỏi làm sao mà cái trạm xăng này giữ được nhà vệ sinh của họ sạch sẽ và tinh tươm đến thế."
* AJ: "Này LB, một cơn lốc xoáy mà quét qua cái nhà vệ sinh đó thì khéo còn giúp nâng cấp thêm được 10.000 đô la ấy chứ."

> 💡 **Giải thích thêm:** "Cowboy logic" là một dạng đối thoại châm biếm bình dân kiểu Mỹ, dùng sự mỉa mai cường điệu để nói về một thực tế phũ phàng. Ở đây, LB nói mỉa (khen phòng vệ sinh sạch nhưng thực chất rất bẩn thỉu), còn AJ đáp lại bằng một câu đùa thậm xưng: nhà vệ sinh đó tồi tàn đến mức nếu có một trận bão quét sạch nó đi thì tài sản thiệt hại bằng không, trái lại còn "lãi" thêm 10.000 USD chi phí cải tạo vì hiện trạng ban đầu còn tệ hại hơn đống đổ nát. Tác giả mượn câu chuyện này để châm biếm cấu trúc phần mềm: nếu mã nguồn bị sắp đặt lộn xộn, tệ hại như "nhà vệ sinh trạm xăng", thì một sự xáo trộn hoặc việc đập đi làm lại từ đầu có khi còn là một sự cải tiến tốt hơn là cố gắng chắp vá.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Chúng ta sẽ tập trung vào cách thức áp dụng các Module trong DDD. Việc liên tục suy ngẫm về mục đích của từng Entity, Value Object, Service và Event cụ thể trong mô hình sẽ mang lại lợi ích lớn cho thiết kế Module. Hãy cùng xem qua các ví dụ về thiết kế Module có chủ đích và thấu đáo.

## Basic Module Naming Conventions

Trong cả Java và C#, tên của các Module đều phản ánh cấu trúc phân cấp (1). Mỗi cấp trong hệ thống phân cấp được ngăn cách bởi dấu chấm (`.`). Hệ thống phân cấp tên thường bắt đầu bằng tên của tổ chức tạo ra nó, kết hợp với tên miền Internet của họ. Khi tên miền Internet được sử dụng, nó thường khởi đầu bằng tên miền cấp cao nhất (`top-level domain`), tiếp theo là tên miền của tổ chức:

1. Sẽ có một số điểm khác biệt nhất định giữa Java package và C# namespace. Chẳng hạn, nếu đang phát triển bằng C#, bạn vẫn có thể sử dụng nội dung này làm chỉ dẫn, nhưng bạn sẽ cần điều chỉnh lại sao cho phù hợp với ngôn ngữ lập trình và nền tảng cụ thể của mình.

```
com.saasovation // Java
SaaSOvation     // C#

```

Việc sử dụng các tên cấp cao nhất có tính duy nhất sẽ ngăn chặn xung đột không gian tên (`namespace collision`) với các Module của bên thứ ba được sử dụng trong dự án của bạn, hoặc các xung đột phát sinh khi mã nguồn của bạn được các bên khác tiêu thụ. Nếu có thắc mắc về các quy ước cơ bản nhất, bạn có thể tham khảo tiêu chuẩn chính thức (2).

Rất có thể tổ chức của bạn đã thống nhất về một quy ước đặt tên Module cấp cao nhất. Tốt nhất là nên duy trì tính nhất quán đó.

## Module Naming Conventions for the Model

Phần phân đoạn tiếp theo của tên Module sẽ xác định Bounded Context. Việc đặt phân đoạn này dựa trên tên của Bounded Context là một lựa chọn sáng suốt.

Dưới đây là cách các nhóm phát triển tại SaaSOvation đặt tên cho các Module này:

```
com.saasovation.identityaccess
com.saasovation.collaboration
com.saasovation.agilepm

```

Họ từng cân nhắc sử dụng các tên sau, nhưng chúng mang lại rất ít giá trị gia tăng so với các tên Module phía trên, nếu không muốn nói là chẳng có gì. Dù chúng phản ánh chính xác từng chữ tên Context, chúng lại có khả năng tạo ra sự rườm rà không cần thiết:

```
com.saasovation.identityandaccess
com.saasovation.agileprojectmanagement

```

Một chi tiết thú vị nữa là họ không sử dụng tên sản phẩm thương mại (thương hiệu) của mình trong tên Module. Tên thương hiệu có thể thay đổi, và đôi khi tên sản phẩm có rất ít hoặc không có mối liên hệ trực tiếp nào với các Bounded Context nền tảng bên dưới. Điều quan trọng hơn là phải nhận diện Context bằng đúng tên gọi chuyên môn mà đội ngũ phát triển cùng nhau thảo luận. Mục tiêu là phản ánh chân thực Ubiquitous Language. Nếu nhóm sử dụng các tên sau đây, nó sẽ không giúp họ đạt được mục tiêu đó:

2. http://java.sun.com/docs/books/jls/second_edition/html/packages.doc.html#26639.

```
com.saasovation.idovation
com.saasovation.collabovation
com.saasovation.projectovation

```

Tên Module đầu tiên, `com.saasovation.idovation`, hầu như không có mối liên hệ nào với Bounded Context của nó. Tên thứ hai thì khá gần gũi. Tên thứ ba gần như tệ ngang tên thứ nhất, dẫu có nhỉnh hơn đôi chút vì ít ra nó còn chứa từ `project`. Dẫu vậy, nhóm đã quyết định rằng những cái tên này không tạo ra được một sự liên tưởng tinh thần hiển nhiên, trực quan tới các Bounded Context tương ứng. Hơn thế nữa, nếu bộ phận marketing quyết định phải thay đổi bất kỳ tên sản phẩm nào — có thể do vi phạm thương hiệu hoặc không tương thích về mặt văn hóa — các tên Module này sẽ hoàn toàn bị lỗi thời. Vì vậy, nhóm quyết định gắn bó với bộ tên đầu tiên.

Tiếp theo, họ bổ sung thêm một định từ (`qualifier`) quan trọng. Nó chỉ rõ rằng Module cụ thể này nằm trong phạm vi miền nghiệp vụ (`domain`):

```
com.saasovation.identityaccess.domain
com.saasovation.collaboration.domain
com.saasovation.agilepm.domain

```

Quy ước này hoàn toàn tương thích với Kiến trúc Phân lớp (`Layers Architecture` (4)) truyền thống và Kiến trúc Lục giác (`Hexagonal Architecture` (4)). Ngày nay, một hệ thống sử dụng phân lớp thông thường sẽ quản lý chúng theo phong cách Lục giác, sử dụng kỹ thuật tiêm phụ thuộc (`injection`). Với Kiến trúc Lục giác, bạn có một phần "bên trong" (`inside`) của ứng dụng, bao gồm phần domain. Điều này cũng sẽ tương tự với các phong cách kiến trúc khác.

Ngăn chứa `domain` có thể không chứa bất kỳ interface hay class nào mà chỉ đóng vai trò như một thùng chứa cho các Module ở cấp thấp hơn. Dưới đây là cấp phân tầng tiếp theo:

```
com.saasovation.identityaccess.domain.model
com.saasovation.collaboration.domain.model
com.saasovation.agilepm.domain.model

```

Đây là nơi các lớp của mô hình bắt đầu được định nghĩa. Cấp package này có thể chứa các interface tái sử dụng và các abstract class.

SaaSOvation thường đặt vào Module này các interface chung, chẳng hạn như những interface dùng cho việc xuất bản Event, cùng các abstract class cơ sở cho Entity và Value Object:

```
ConcurrencySafeEntity
DomainEvent
DomainEventPublisher
DomainEventSubscriber
DomainRegistry
Entity
IdentifiedDomainObject
IdentifiedValueObject

```

Nếu bạn ưa chuộng phong cách đặt các Domain Service (`Domain Services` - các dịch vụ xử lý logic miền không gắn liền với một Entity cụ thể) bên ngoài Module `domain.model`, bạn có thể tạo một Module đồng cấp với nó:

```
com.saasovation.identityaccess.domain.service
com.saasovation.collaboration.domain.service
com.saasovation.agilepm.domain.service

```

Việc đặt các Domain Service ở đây không phải là yêu cầu bắt buộc. Lựa chọn này khả dụng nếu bạn xem chúng như một dạng tầng phụ dịch vụ có độ chi tiết trung bình (`medium-grained service mini-layer`) nằm phía trên mô hình, hoặc như một chiếc vòng bao quanh nó [Evans, tr. 108, "Granularity"]. Tuy nhiên, hãy lưu ý rằng cách tiếp cận này có thể nhanh chóng dẫn tới Mô hình Miền Thiếu máu (`Anemic Domain Model` - mô hình chỉ chứa dữ liệu/getter/setter mà thiếu vắng hành vi nghiệp vụ), vấn đề sẽ được thảo luận chi tiết trong chương Services (7).

Trong trường hợp bạn không phân chia model và services thành hai package riêng biệt, bạn có thể bỏ qua Module `model` và đặt trực tiếp tất cả các Module mô hình ngay dưới `domain`:

```
com.saasovation.identityaccess.domain.conceptname

```

Cách này loại bỏ được một cấp package có vẻ thừa thãi. Thế nhưng, điều gì sẽ xảy ra nếu sau này bạn quyết định đưa một vài Domain Service vào một sub-Module `domain.service`? Khi đó, rất có thể bạn sẽ cảm thấy vô cùng tiếc nuối vì trước đó đã không tạo sẵn sub-Module `domain.model`.

Nhưng còn có một yếu tố ảnh hưởng đến việc đặt tên thậm chí còn quan trọng hơn cần phải cân nhắc. Hãy nhớ rằng chúng ta không phát triển một domain. Bản thân Miền (`Domain` (2)) là toàn bộ lĩnh vực tri thức/chuyên môn nghiệp vụ thực tế của doanh nghiệp nơi chúng ta đang làm việc. Thứ chúng ta thiết kế và lập trình triển khai là *mô hình của một miền* (`a model of a domain`). Do đó, khi đặt tên cho Module tối thượng chứa mô hình, `domain.model` tỏ ra là lựa chọn thỏa đáng nhất. Dẫu vậy, quyền quyết định cuối cùng vẫn thuộc về đội ngũ của bạn.

## Modules of the Agile Project Management Context

Miền Cốt lõi (`Core Domain` (2) - phần lõi tạo nên lợi thế cạnh tranh của phần mềm) hiện tại của SaaSOvation là `Agile Project Management Context`, do đó việc xem xét cách thức các Module của nó được thiết kế là hoàn toàn hợp lý.

Nhóm ProjectOvation đã chọn 3 Module cấp cao nhất: `tenant`, `team`, và `product`. Dưới đây là Module đầu tiên:

```
com.saasovation.agilepm.domain.model.tenant
<<value object>> TenantId

```

Nội dung bên trong nó là một Value Object đơn giản, `TenantId`, nắm giữ định danh duy nhất của một tenant cụ thể (`tenant` - khách thuê hệ thống trong kiến trúc đa người thuê multi-tenant), bắt nguồn từ `Identity and Access Context`. Trong trường hợp của Module này, hầu như tất cả các Module khác trong mô hình đều sẽ phụ thuộc vào nó. Nó đóng vai trò cốt yếu để phân tách các đối tượng của tenant này với tenant khác. Tuy nhiên, mối phụ thuộc này là phi chu trình (`acyclic`). Module `tenant` không hề phụ thuộc ngược lại vào các Module khác.

Module `team` chứa các Aggregate và một Domain Service dùng để quản lý các nhóm phát triển sản phẩm:

```
com.saasovation.agilepm.domain.model.team
<<service>> MemberService
<<aggregate root>> ProductOwner
<<aggregate root>> Team
<<aggregate root>> TeamMember

```

Có 3 Aggregate và một interface Domain Service. Lớp `Team` chứa một instance `ProductOwner` và một tập hợp chứa số lượng tùy ý các instance `TeamMember`. Các instance `ProductOwner` và `TeamMember` được khởi tạo bởi `MemberService`. Cả 3 Thực thể Gốc của Cụm (`Aggregate Root Entities` - thực thể đóng vai trò cửa ngõ quản lý toàn bộ cụm Aggregate) đều tham chiếu đến `TenantId` của Module `tenant`:

```java
package com.saasovation.agilepm.domain.model.team;

import com.saasovation.agilepm.domain.model.tenant.TenantId;

public class Team extends ConcurrencySafeEntity {
    private TenantId tenantId;
    ...
}

```

`MemberService` là một cổng giao tiếp phía trước (`front end`) cho một Lớp Chống Suy thoái (`Anticorruption Layer` (3) - tầng kỹ thuật cách ly mô hình miền nội bộ khỏi các mô hình bên ngoài) nhằm đồng bộ hóa các thành viên trong nhóm sản phẩm với các danh tính và vai trò lấy từ `Identity and Access Context`. Quá trình đồng bộ diễn ra ngầm trong nền (`out of band`), tách biệt với các luồng yêu cầu thông thường của người dùng. Service này hoạt động chủ động, tạo mới các thành viên ngay khi

## MODULES OF THE AGILE PROJECT MANAGEMENT CONTEXT

họ được đăng ký ở Context từ xa. Quá trình đồng bộ đạt tính nhất quán cuối cùng (`eventually consistent`) với hệ thống từ xa nhưng độ trễ chỉ là một khoảng thời gian ngắn so với những thay đổi thực tế diễn ra ở phía bên kia. Nó cũng cập nhật các chi tiết của thành viên, chẳng hạn như họ tên và địa chỉ email, khi cần thiết.

`Agile Project Management Context` có một Module cha tên là `product` cùng 3 Module con:

```
com.saasovation.agilepm.domain.model.product
<<aggregate root>> Product
...
com.saasovation.agilepm.domain.model.product.backlogitem
<<aggregate root>> BacklogItem
...
com.saasovation.agilepm.domain.model.product.release
<<aggregate root>> Release
...
com.saasovation.agilepm.domain.model.product.sprint
<<aggregate root>> Sprint
...

```

Đây chính là nơi phần mô hình cốt lõi của Scrum ngự trị. Tại đây bạn sẽ tìm thấy các Aggregate `Product`, `BacklogItem`, `Release`, và `Sprint`. Bạn sẽ thấy trong chương Aggregates (10) lý do tại sao các khái niệm này lại được mô hình hóa thành các Aggregate riêng biệt.

Nhóm rất thích cách các Module này được đọc lên một cách tự nhiên theo Ubiquitous Language: "product" (sản phẩm), "product backlog item" (hạng mục tồn đọng của sản phẩm), "product release" (đợt phát hành sản phẩm), và "product sprint" (sprint của sản phẩm).

Với số lượng ít ỏi các Aggregate có quan hệ mật thiết như vậy — chỉ có 4 — tại sao nhóm không gom cả 4 vào chung Module `product`? Phần hiển thị ở trên chưa liệt kê toàn bộ các thành phần khác của Aggregate, chẳng hạn như Entity `ProductBacklogItem` chứa bên trong `Product`, Entity `Task` chứa bên trong `BacklogItem`, `ScheduledBacklogItem` chứa bên trong `Release`, và `CommittedBacklogItem` được chứa

bên trong `Sprint`. Còn có các Entity và Value Object khác được nắm giữ bởi từng loại Aggregate. Ngoài ra, còn có một lượng lớn Domain Event được xuất bản bởi một số Aggregate. Tổng cộng lại, việc nhồi nhét gần 60 class và interface vào trong một Module duy nhất sẽ khiến nó trở nên vô cùng đông đúc, ngột ngạt, tạo ra ấn tượng rõ rệt về sự thiếu tổ chức. Nhóm đã lựa chọn tính ngăn nắp, có tổ chức thay vì quá bận tâm đến các lo ngại về liên kết chéo Module (`cross-Module coupling`).

Tương tự như `ProductOwner`, `Team`, và `TeamMember`, toàn bộ các kiểu Aggregate `Product`, `BacklogItem`, `Release`, và `Sprint` đều tham chiếu tới `TenantId`. Đồng thời còn xuất hiện thêm các mối phụ thuộc bổ sung. Hãy xem xét `Product`:

```java
package com.saasovation.agilepm.domain.model.product;

import com.saasovation.agilepm.domain.model.tenant.TenantId;

public class Product extends ConcurrencySafeEntity {
    private ProductId productId;
    private TeamId teamId;
    private TenantId tenantId;
    ...
}

```

Hãy nhìn tiếp vào `BacklogItem`:

```java
package com.saasovation.agilepm.domain.model.product.backlogitem;

import com.saasovation.agilepm.domain.model.tenant.TenantId;

public class BacklogItem extends ConcurrencySafeEntity {
    private BacklogItemId backlogItemId;
    private ProductId productId;
    private TeamId teamId;
    private TenantId tenantId;
    ...
}

```

Các tham chiếu tới `TenantId` và `TeamId` là các phụ thuộc phi chu trình; chúng chỉ đi theo một chiều duy nhất. Tuy nhiên, dẫu việc `BacklogItem` tham chiếu tới `ProductId` thoạt nhìn có vẻ tạo thành một phụ thuộc đơn hướng từ Module `backlogItem` sang `product`, nhưng thực chất nó lại là hai chiều (`bidirectional`). Mỗi `Product` đóng vai trò như một Factory (`Factory` - mẫu khởi tạo đối tượng) để tạo ra các instance `BacklogItem` (cũng như `Release` và `Sprint`). Do đó, quan hệ phụ thuộc diễn ra theo cả hai hướng. Dù vậy, 3 sub-Module này đều là con của `product`, và chúng ta hoàn toàn có thể nới lỏng các quy tắc về phụ thuộc một chút. Ở đây, sự đánh đổi là ưu tiên sức mạnh tổ chức hơn là sự phụ thuộc. Một lần nữa, `BacklogItem`, `Release`, và `Sprint` đều là những khái niệm con tự nhiên và tất yếu của `Product`, do đó việc cố gắng bẻ nhỏ các khái niệm này vượt ra ngoài các ranh giới Aggregate là không mang lại nhiều ý nghĩa.

Dẫu vậy, liệu nhóm có thể đạt được sự liên kết lỏng lẻo hơn giữa các thành phần này bằng cách sử dụng một kiểu định danh chung (`generic identity type`), nơi mà `BacklogItem`, `Release`, và `Sprint` đều sẽ tham chiếu đến `Product` của chúng theo cách không ràng buộc chặt chẽ hay không?

```java
public class BacklogItem extends ConcurrencySafeEntity {
    private Identity backlogItemId;
    private Identity productId;
    private Identity teamId;
    private Identity tenantId;
    ...
}

```

Đúng là nhóm có thể đạt được mức độ phụ thuộc lỏng lẻo hơn. Tuy nhiên, nó cũng sẽ mở ra nguy cơ phát sinh lỗi tiềm ẩn trong code khi mà các kiểu `Identity` khác nhau không thể phân biệt được với nhau về mặt kiểu dữ liệu (`type safety`).

`Agile Project Management Context` sẽ tiếp tục tiến hóa. SaaSOvation có kế hoạch hỗ trợ các phương pháp tiếp cận và công cụ Agile khác. Việc làm này chắc chắn sẽ tác động tới các Module hiện tại, chí ít là thúc đẩy việc tạo mới các Module, nhưng rất có thể cũng sẽ kéo theo những thay đổi đối với các Module hiện có. Nhóm phát triển, với tinh thần agile, đã cam kết sẽ refactor các Module với sự cẩn trọng và trách nhiệm cao nhất.

Tiếp theo, hãy cùng xem xét cách Module được sử dụng ở các vị trí khác xuyên suốt mã nguồn của hệ thống.

## Modules in Other Layers

Bất kể Kiến trúc (4) bạn chọn là gì, bạn sẽ luôn phải tạo và đặt tên cho các Module của những thành phần không thuộc mô hình bên trong kiến trúc của mình. Ở đây chúng ta thảo luận một số lựa chọn cho một Kiến trúc Phân lớp (4) kinh điển, nhưng chúng cũng hoàn toàn có thể áp dụng được cho các phong cách kiến trúc khác.

Trong một Kiến trúc Phân lớp điển hình được sử dụng cho ứng dụng sở hữu một domain model, bạn sẽ xếp chồng các tầng như sau: Giao diện người dùng (`User Interface`), Ứng dụng (`Application`), Miền nghiệp vụ (`Domain`), Hạ tầng (`Infrastructure`). Tùy thuộc vào loại thành phần trong từng tầng, được quyết định bởi nhu cầu của ứng dụng, các Module bên trong mỗi tầng sẽ có sự khác nhau.

Để bắt đầu, hãy xem xét Tầng Giao diện Người dùng (`User Interface Layer` (14)) và hệ quả của việc hỗ trợ các tài nguyên RESTful (`RESTful resources`). Có khả năng các tài nguyên của bạn sẽ được sử dụng để phục vụ giao diện đồ họa người dùng (`GUI`) và các hệ thống client, tạo ra các trạng thái biểu diễn (`representational state`) dưới dạng XML, JSON và HTML. Tuy nhiên, trong trường hợp phục vụ GUI, các tài nguyên RESTful sẽ không / không nên tạo ra các biểu diễn bao hàm cả bố cục hiển thị (`presentation layout`). Thay vào đó, chúng sẽ chỉ tạo ra các biểu diễn dữ liệu thuần túy ở nhiều định dạng đánh dấu (XML, HTML) và định dạng tuần tự hóa (XML, JSON, Protocol Buffers). Mọi bố cục đồ họa mà các trạng thái biểu diễn này được áp dụng ở phía client sẽ đến từ một kênh khác. Do đó, trong Tầng Giao diện Người dùng hỗ trợ REST, bạn có thể chọn có ít nhất hai Module được đặt tên như sau:

com.saasovation.agilepm.resources
com.saasovation.agilepm.resources.view

Các tài nguyên RESTful được duy trì trong package `resources`. Các mối quan tâm thuần túy về mặt trình bày (`presentation`) được cung cấp bởi các thành phần trong sub-package `view` (hoặc `presentation`, nếu bạn thích). Tùy thuộc vào số lượng tài nguyên dựa trên REST mà hệ thống yêu cầu, bạn có thể có một số sub-Module bên dưới mỗi Module chính. Lưu ý rằng một class cung cấp tài nguyên (`resource provider class`) có thể hỗ trợ nhiều URI, vì vậy bạn có thể có đủ ít các class cung cấp tài nguyên để gom tất cả chúng trong Module chính. Việc có cần mô-đun hóa chúng sâu hơn nữa hay không là một quyết định rất dễ dàng một khi bạn đã xác định được các yêu cầu tài nguyên thực tế của mình.

Tầng Ứng dụng (`Application Layer`) có thể có các Module khác, có thể bao gồm một Module cho mỗi loại service:

```
com.saasovation.agilepm.application.team
com.saasovation.agilepm.application.product
...
com.saasovation.agilepm.application.tenant

```

Tương tự như các nguyên tắc thiết kế tài nguyên dịch vụ RESTful, các service trong Application Layer chỉ nên chia thành các sub-Module nếu việc đó thực sự hữu ích. Ví dụ, trong `Identity and Access Context`, chỉ có một vài Application Service, và nhóm đã chọn giữ nguyên chúng trong Module chính:

```
com.saasovation.identityaccess.application

```

Bạn cũng có thể quyết định theo hướng thiết kế mô-đun hóa chi tiết hơn. Điều đó cũng hoàn toàn ổn. Khi bạn có nhiều hơn một vài service, chẳng hạn như khoảng nửa tá trở lên, việc phân chia mô-đun hóa chúng cẩn thận hơn có thể sẽ giúp ích rất nhiều.

## Module before Bounded Context

Chúng ta cần phải cân nhắc hết sức kỹ lưỡng trước nhu cầu cảm tính về việc chia tách các đối tượng domain model có tính gắn kết thành các mô hình riêng biệt, hay giữ chúng ở cùng nhau. Đôi khi đặc điểm ngôn ngữ của miền nghiệp vụ thực tế, đích thực sẽ tự hiển hiện rõ ràng trước mắt bạn, nhưng đôi khi các thuật ngữ lại khá mờ nhạt và mơ hồ. Trong những trường hợp mà thuật ngữ chưa rõ ràng và không chắc chắn liệu có nên tạo lập các ranh giới ngữ cảnh hay không, trước hết hãy xem xét khả năng giữ chúng lại cùng nhau. Cách tiếp cận này sẽ sử dụng ranh giới mỏng hơn của Module để phân tách, thay vì dùng ranh giới dày hơn của Bounded Context.

Điều này không có nghĩa là chúng ta hiếm khi sử dụng nhiều Bounded Context. Ranh giới giữa các mô hình luôn hoàn toàn chính đáng khi tính chất ngôn ngữ nghiệp vụ đòi hỏi điều đó. Điều bạn cần đúc rút ở đây là Bounded Context không được sinh ra để dùng làm vật thay thế cho Module. Hãy sử dụng Module để tổ chức các đối tượng miền có tính gắn kết, và để tách biệt những đối tượng không gắn kết hoặc ít gắn kết với nhau.

## Wrap-Up

Chúng ta vừa xem xét quá trình mô-đun hóa domain model, lý do tại sao nó lại quan trọng và cách thức triển khai ra sao.

* Bạn đã nhận thấy sự khác biệt giữa Module truyền thống và phương pháp tiếp cận mô-đun hóa triển khai mới hơn.
* Bạn đã học được tầm quan trọng của việc đặt tên Module theo Ubiquitous Language.
* Bạn đã thấy cách thức thiết kế Module sai lầm, thậm chí là máy móc, thực sự bóp nghẹt khả năng sáng tạo mô hình như thế nào.
* Bạn đã xem xét cách các Module của Agile PM Context được thiết kế, và lý do đằng sau các lựa chọn cụ thể.
* Bạn đã nhận được những chỉ dẫn hữu ích về Module tại các khu vực của hệ thống nằm ngoài mô hình miền.
* Cuối cùng, bạn có thêm một vài lưu ý về việc ưu tiên cân nhắc sử dụng Module thay vì vội vàng tạo các Bounded Context mới, trừ phi ngữ nghĩa nghiệp vụ bắt buộc phải chia tách ở mức độ thô hơn.

Tiếp theo, chúng ta sẽ đi sâu một cách thực sự toàn diện vào một trong những công cụ mô hình hóa ít được hiểu đúng nhất của DDD: Aggregates.

Trang này được cố ý để trống

## Chapter 10

## Aggregates

Vũ trụ được tạo nên từ một tập hợp các đối tượng vĩnh cửu kết nối với nhau bằng các mối quan hệ nhân quả độc lập với chủ thể và được đặt trong không gian cũng như thời gian khách quan.

— Jean Piaget

Việc gom cụm các Entity (5) và Value Object (6) thành một Aggregate với một ranh giới nhất quán (`consistency boundary`) được gọt giũa cẩn thận thoạt nhìn có vẻ là một công việc nhanh chóng, nhưng trong số tất cả các chỉ dẫn chiến thuật của DDD, mẫu hình này lại là một trong những phần bị hiểu sai nhiều nhất.

## Road Map to This Chapter

* Cùng với SaaSOvation, trải nghiệm những hậu quả tiêu cực của việc mô hình hóa sai lầm các Aggregate.
* Học cách thiết kế dựa trên Các Quy Tắc Thực Nghiệm Của Aggregate (`Aggregate Rules of Thumb`) như một tập hợp các hướng dẫn thực hành tốt nhất.
* Nắm vững cách mô hình hóa các bất biến nghiệp vụ đích thực (`true invariants` - các quy tắc logic nghiệp vụ luôn bắt buộc phải đúng tại mọi thời điểm) bên trong các ranh giới nhất quán dựa theo các quy tắc nghiệp vụ thực tế.
* Cân nhắc những lợi thế to lớn của việc thiết kế các Aggregate nhỏ gọn.
* Hiểu rõ lý do tại sao bạn nên thiết kế các Aggregate tham chiếu đến các Aggregate khác chỉ thông qua định danh (`identity`).
* Khám phá tầm quan trọng của việc sử dụng tính nhất quán cuối cùng (`eventual consistency`) bên ngoài ranh giới Aggregate.
* Nắm bắt các kỹ thuật triển khai Aggregate, bao gồm nguyên lý "Hãy ra lệnh, đừng hỏi" (`Tell, Don't Ask`) và Định luật Demeter (`Law of Demeter` - nguyên lý tri thức tối thiểu, giới hạn mức độ tương tác sâu vào đối tượng bên trong).

Để bắt đầu, việc xem xét một số câu hỏi phổ biến có thể sẽ rất hữu ích. Liệu Aggregate có đơn thuần chỉ là một cách để gom cụm một đồ thị các đối tượng có quan hệ mật thiết dưới một đối tượng cha chung? Nếu đúng như vậy, liệu có giới hạn thực tế nào đối với số lượng đối tượng được phép cư ngụ trong đồ thị đó không? Vì một thể hiện Aggregate có thể tham chiếu tới các thể hiện Aggregate khác, liệu các mối liên kết có thể được điều hướng sâu (`navigated deeply`), sửa đổi nhiều đối tượng khác nhau dọc đường đi hay không? Và khái niệm về các invariant cùng ranh giới tính nhất quán thực chất là gì? Chính câu trả lời cho câu hỏi cuối cùng này sẽ tác động sâu sắc nhất tới câu trả lời cho tất cả các câu hỏi còn lại.

Có nhiều cách dẫn tới việc mô hình hóa Aggregate sai lầm. Chúng ta có thể rơi vào cái bẫy thiết kế theo hướng thuận tiện cho việc ghép nối thành phần (`compositional convenience`) và biến chúng thành những cụm quá lớn. Ở đầu kia của thái cực, chúng ta lại có thể bóc trần trụi mọi Aggregate, và kết quả là thất bại trong việc bảo vệ các invariant đích thực. Như chúng ta sẽ thấy, điều tối quan trọng là chúng ta phải tránh cả hai thái cực này, và thay vào đó hãy chú tâm vào các quy tắc nghiệp vụ.

## Using Aggregates in the Scrum Core Domain

Chúng ta sẽ xem xét kỹ lưỡng cách thức Aggregate được sử dụng bởi SaaSOvation, và cụ thể là bên trong ứng dụng mang tên ProjectOvation thuộc `Agile Project Management Context`. Ứng dụng này tuân theo mô hình quản lý dự án Scrum truyền thống, bao gồm đầy đủ sản phẩm (`product`), chủ sản phẩm (`product owner`), đội ngũ (`team`), các hạng mục tồn đọng (`backlog items`), các đợt phát hành theo kế hoạch (`planned releases`), và các chu kỳ nước rút (`sprints`). Nếu bạn hình dung về Scrum ở trạng thái phong phú nhất, thì đó chính là đích đến của ProjectOvation; đây là một miền nghiệp vụ rất đỗi quen thuộc với đa số chúng ta. Các thuật ngữ của Scrum tạo nên điểm khởi đầu cho Ubiquitous Language (1). Vì đây là một ứng dụng dạng thuê bao trả phí được lưu trữ theo mô hình phần mềm dưới dạng dịch vụ (`SaaS`), mỗi tổ chức đăng ký sử dụng sẽ được ghi nhận là một tenant, thêm một thuật ngữ nữa trong Ubiquitous Language của chúng ta.

Công ty đã quy tụ được một đội ngũ gồm các chuyên gia Scrum và các lập trình viên đầy tài năng. Tuy nhiên, vì kinh nghiệm của họ với DDD còn khá hạn chế, nhóm sẽ vấp phải một số sai lầm với DDD khi phải leo lên một đường cong học tập (`learning curve`) đầy gian nan. Họ sẽ trưởng thành dần bằng cách rút ra bài học từ chính những trải nghiệm

với Aggregate, và chúng ta cũng có thể học hỏi từ đó. Những khó khăn chật vật của họ có thể giúp chúng ta nhận diện và thay đổi những tình huống bất lợi tương tự mà chính chúng ta từng tạo ra trong phần mềm của mình.

Các khái niệm của miền nghiệp vụ này, cùng với các yêu cầu về hiệu năng và khả năng mở rộng quy mô (`scalability`), phức tạp hơn bất kỳ điều gì nhóm từng đối mặt trước đây trong Core Domain ban đầu (2) là `Collaboration Context`. Để giải quyết những thách thức này, một trong những công cụ chiến thuật của DDD mà họ sẽ triển khai chính là Aggregate.

Nhóm nên lựa chọn các cụm đối tượng tốt nhất như thế nào? Mẫu hình Aggregate thảo luận về cấu thành (`composition`) và ám chỉ tới tính che giấu thông tin (`information hiding`), những điều mà nhóm hiểu rất rõ cách đạt được. Mẫu hình cũng bàn về các ranh giới nhất quán và các giao dịch (`transactions`), nhưng họ lại chưa từng bận tâm quá mức về điều đó. Cơ chế lưu trữ bền vững mà họ chọn sẽ giúp quản lý các lượt commit nguyên tử cho dữ liệu. Tuy nhiên, đó lại là một sự hiểu lầm chí mạng về chỉ dẫn của mẫu hình, khiến họ bị thụt lùi. Dưới đây là những gì đã xảy ra. Nhóm đã xem xét các phát biểu sau trong Ubiquitous Language:

* Các Product có các backlog item, các release, và các sprint.
* Các backlog item mới của sản phẩm được lập kế hoạch.

## USING AGGREGATES IN THE SCRUM CORE DOMAIN

* Các release mới của sản phẩm được lên lịch.
* Các sprint mới của sản phẩm được lên lịch.
* Một backlog item đã lập kế hoạch có thể được lên lịch cho một release.
* Một backlog item đã lên lịch có thể được cam kết (`committed`) vào một sprint.

Từ những điều này, họ hình dung ra một mô hình và bắt tay vào lần thử thiết kế đầu tiên. Hãy xem mọi chuyện diễn ra như thế nào.

## First Attempt: Large-Cluster Aggregate

Nhóm đã đặt rất nhiều sức nặng vào cụm từ "Products have" (Các sản phẩm có...) trong phát biểu đầu tiên, điều này đã chi phối nỗ lực ban đầu của họ khi thiết kế Aggregate cho miền nghiệp vụ này.

Đối với một số người, cụm từ đó nghe như thể là quan hệ hợp thành (`composition`), rằng các đối tượng cần phải được liên kết chằng chịt với nhau như một đồ thị đối tượng (`object graph`). Việc duy trì vòng đời của các đối tượng này cùng nhau được coi là tối quan trọng. Hệ quả là các lập trình viên đã bổ sung các quy tắc nhất quán sau vào bản đặc tả yêu cầu:

* Nếu một backlog item đã được commit vào một sprint, chúng ta tuyệt đối không được phép xóa nó khỏi hệ thống.
* Nếu một sprint đang có các backlog item đã commit, chúng ta tuyệt đối không được phép xóa sprint đó khỏi hệ thống.
* Nếu một release đang có các backlog item đã lên lịch, chúng ta tuyệt đối không được phép xóa release đó khỏi hệ thống.
* Nếu một backlog item đã được lên lịch cho một release, chúng ta tuyệt đối không được phép xóa nó khỏi hệ thống.

Kết quả là, ban đầu `Product` được mô hình hóa thành một Aggregate cực lớn. Đối tượng Gốc (`Root object`), `Product`, nắm giữ toàn bộ các thể hiện `BacklogItem`, toàn bộ `Release`, và toàn bộ `Sprint` gắn liền với nó. Thiết kế giao diện lập trình được xây dựng để bảo vệ tất cả các phần tử con khỏi việc vô tình bị xóa bỏ bởi phía client.

Thiết kế này được thể hiện trong đoạn mã dưới đây, và dưới dạng biểu đồ UML trong Hình 10.1:

```java
public class Product extends ConcurrencySafeEntity {

```

```java
    private Set<BacklogItem> backlogItems;
    private String description;
    private String name;
    private ProductId productId;
    private Set<Release> releases;

```
